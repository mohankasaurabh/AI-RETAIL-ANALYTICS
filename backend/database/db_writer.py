"""
=====================================================
Batched asynchronous DB writer
=====================================================

Concurrent camera workers produce high-frequency rows
(movement points, samples, snapshots). Committing per-frame
from each thread against a shared Session is both slow and
thread-unsafe.

This writer accepts ORM instances on a thread-safe queue and a
single background thread flushes them in batches using its own
scoped session. Start it once at app startup.

Usage:
    from backend.database.db_writer import db_writer
    db_writer.start()
    db_writer.enqueue(MovementPoint(camera_id=1, x=10, y=20))
"""

import threading
import queue
import time

from backend.database.db import ScopedSession


class BatchedDBWriter:

    def __init__(self, batch_size=200, flush_interval=1.0):
        self._q = queue.Queue()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._thread = None
        self._running = False

    # ---- public API ----

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, name="db-writer", daemon=True
        )
        self._thread.start()
        print("[DB-WRITER] started")

    def stop(self):
        self._running = False

    def enqueue(self, obj):
        """Queue a single ORM instance for insertion."""
        if obj is not None:
            self._q.put(obj)

    def enqueue_many(self, objs):
        for o in objs:
            self.enqueue(o)

    # ---- internals ----

    def _loop(self):
        while self._running:
            batch = self._drain()
            if batch:
                self._flush(batch)
            else:
                time.sleep(self._flush_interval)

    def _drain(self):
        batch = []
        try:
            # block briefly for the first item, then grab whatever is ready
            first = self._q.get(timeout=self._flush_interval)
            batch.append(first)
            while len(batch) < self._batch_size:
                batch.append(self._q.get_nowait())
        except queue.Empty:
            pass
        return batch

    def _flush(self, batch):
        session = ScopedSession()
        try:
            session.add_all(batch)
            session.commit()
        except Exception as exc:
            session.rollback()
            print(f"[DB-WRITER ERROR] {exc} (dropped {len(batch)} rows)")
        finally:
            ScopedSession.remove()


# global singleton
db_writer = BatchedDBWriter()
