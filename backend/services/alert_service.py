"""
=====================================================
Alert Service
=====================================================

Evaluates live per-camera metrics against thresholds
(occupancy, queue congestion) and raises Alert rows with a
per-(camera,type) cooldown to avoid spam. Camera-offline /
low-FPS alerts are raised directly by CameraWorker.

Called from the Socket.IO broadcast loop (~1 Hz).
"""

import time

from backend.database import repository
from backend.services import settings_service


class AlertService:

    def __init__(self):
        self._cooldown = {}  # (camera_id, type) -> last epoch

    def _fire(self, type_, message, severity, camera_id, cooldown=120):
        key = (camera_id, type_)
        now = time.time()
        if now - self._cooldown.get(key, 0) < cooldown:
            return
        self._cooldown[key] = now
        try:
            repository.add_alert(type_, message, severity=severity, camera_id=camera_id)
        except Exception as exc:
            print(f"[ALERT error] {exc}")

    def evaluate(self, analytics_service):
        cfg = settings_service.get_all()
        if not cfg.get("alerts_enabled", True):
            return

        occ_th = int(cfg.get("alert_occupancy", 20))
        q_th = int(cfg.get("alert_queue_length", 8))

        for camera_id, m in list(analytics_service.cameras.items()):
            if not isinstance(camera_id, int):
                continue  # skip the legacy "default" bucket

            if m.get("occupancy", 0) >= occ_th:
                self._fire(
                    "occupancy",
                    f"High occupancy ({m['occupancy']}) on camera {camera_id}",
                    "warning", camera_id,
                )

            if m.get("queue_length", 0) >= q_th or m.get("queue_status") == "HIGH":
                self._fire(
                    "queue",
                    f"Queue congestion on camera {camera_id}",
                    "warning", camera_id,
                )


alert_service = AlertService()
