"""
=====================================================
Dwell Tracker — per-customer per-zone dwell time
=====================================================

Tracks each customer's (reid_id) current zone and how long
they have been in it. On every zone transition (or when a
customer leaves the frame) it closes the open ZoneVisit,
computes the dwell duration + revisit index, and persists a
ZoneVisit row via the batched DB writer.

Returns the live dwell (seconds) for the in-progress zone so
the pipeline can render it above each person.
"""

import time
from datetime import datetime

from backend.database.db_writer import db_writer
from backend.database.models import ZoneVisit


class DwellTracker:

    def __init__(self, camera_id):
        self.camera_id = camera_id
        # reid_id -> {zone_id, zone_name, entry_t, entry_dt}
        self.active = {}
        # (reid_id, zone_id) -> count
        self.revisits = {}
        # reid_id -> last update epoch (for stale flush)
        self.last_seen = {}

    # =====================================
    # PER-OBJECT UPDATE
    # =====================================

    def update(self, reid_id, zone_id, zone_name):
        now = time.time()
        self.last_seen[reid_id] = now
        cur = self.active.get(reid_id)

        # same zone -> return running dwell
        if cur and cur["zone_id"] == zone_id:
            return now - cur["entry_t"]

        # transition: close previous, open new
        if cur:
            self._close(reid_id, cur, now)

        if zone_id is None:
            # not inside any zone
            self.active.pop(reid_id, None)
            return 0.0

        key = (reid_id, zone_id)
        self.revisits[key] = self.revisits.get(key, 0) + 1
        self.active[reid_id] = {
            "zone_id": zone_id,
            "zone_name": zone_name,
            "entry_t": now,
            "entry_dt": datetime.utcnow(),
        }
        return 0.0

    # =====================================
    # CLOSE / FLUSH
    # =====================================

    def _close(self, reid_id, cur, now):
        if cur.get("zone_id") is None:
            return
        dwell = now - cur["entry_t"]
        # ignore noise (< 0.5s flickers)
        if dwell < 0.5:
            return
        db_writer.enqueue(ZoneVisit(
            customer_id=reid_id,
            zone_id=cur["zone_id"],
            camera_id=self.camera_id,
            entry_time=cur["entry_dt"],
            exit_time=datetime.utcnow(),
            dwell_seconds=round(dwell, 1),
            revisit_index=self.revisits.get((reid_id, cur["zone_id"]), 1),
        ))

    def flush_stale(self, present_ids, max_idle=4.0):
        """Close zone visits for customers no longer in frame."""
        now = time.time()
        for reid_id in list(self.active.keys()):
            if reid_id in present_ids:
                continue
            if now - self.last_seen.get(reid_id, 0) >= max_idle:
                self._close(reid_id, self.active[reid_id], now)
                self.active.pop(reid_id, None)
