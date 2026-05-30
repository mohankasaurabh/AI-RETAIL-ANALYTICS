"""
=====================================================
Customer Session Tracker
=====================================================

Per-camera tracker that opens a CustomerVisit when a ReID
identity first appears and closes it (with dwell) when the
identity leaves the frame. DB writes happen only on these
appear/disappear transitions — never per frame — so the
synchronous repository calls stay cheap.
"""

import time

from backend.database import repository


class CustomerSessionTracker:

    def __init__(self, camera_id):
        self.camera_id = camera_id
        # reid_id -> {visit_id, entry_t, last_t}
        self.active = {}

    def touch(self, reid_id, profile=None):
        now = time.time()
        s = self.active.get(reid_id)
        if s:
            s["last_t"] = now
            return
        # new appearance -> open a visit
        profile = profile or {}
        try:
            vid = repository.open_customer_visit(
                reid_id, self.camera_id,
                age=profile.get("age"),
                gender=profile.get("gender"),
            )
        except Exception as exc:
            print(f"[CUSTOMER open error] {exc}")
            vid = None
        self.active[reid_id] = {"visit_id": vid, "entry_t": now, "last_t": now}

    def flush_stale(self, present_ids, max_idle=5.0):
        now = time.time()
        for reid_id in list(self.active.keys()):
            if reid_id in present_ids:
                continue
            s = self.active[reid_id]
            if now - s["last_t"] >= max_idle:
                if s.get("visit_id") is not None:
                    try:
                        repository.close_customer_visit(
                            s["visit_id"], now - s["entry_t"]
                        )
                    except Exception as exc:
                        print(f"[CUSTOMER close error] {exc}")
                self.active.pop(reid_id, None)
