"""
=====================================================
Per-camera AI Pipeline
=====================================================

Instance-per-camera refactor of the monolithic FrameProcessor.
Each CameraWorker owns one Pipeline, so tracker/zone/heatmap
state is independent per stream. The shared ReID registry
(cross-camera identity) is the only shared component.

Differences vs. the legacy FrameProcessor:
- model toggles (models_enabled) — skip ReID/demographics/heatmap/zones
- all analytics writes are namespaced by camera_id
- demographics keyed by persistent reid_id (fixes track_id orphaning)
- demographics throttled (runs every N frames)
- writes MovementPoint(camera_id, customer_id) for the new schema
"""

import cv2

from ai_engine.tracking.tracker import CustomerTracker
from ai_engine.tracking.tracking_utils import (
    draw_tracking_box, draw_centroid, draw_trajectory,
    get_centroid, update_trajectory,
)
from ai_engine.demographics.age_gender import DemographicsAnalyzer
from ai_engine.analytics.heatmap_generator import HeatmapGenerator
from ai_engine.analytics.zone_analytics import ZoneAnalytics
from ai_engine.analytics.queue_analytics import QueueAnalytics
from ai_engine.analytics.customer_journey import CustomerJourney
from ai_engine.analytics.dwell_time import DwellTracker
from ai_engine.reid.reid_model import ReIDManager

from backend.services.customer_session import CustomerSessionTracker

from backend.services.analytics_service import analytics_service
from backend.database.db_writer import db_writer
from backend.database.models import MovementPoint, DemographicSample


DEFAULT_MODELS = {
    "detection": True, "tracking": True, "reid": True,
    "demographics": True, "heatmap": True, "zones": True,
}


class Pipeline:

    def __init__(self, camera_id, models_enabled=None, demo_interval=5):
        self.camera_id = camera_id
        self.models = {**DEFAULT_MODELS, **(models_enabled or {})}
        self.demo_interval = demo_interval
        self.frame_idx = 0
        self._cached_demographics = []

        # core: detection + tracking always on (the platform's reason to exist)
        self.tracker = CustomerTracker()

        self.reid_manager = ReIDManager() if self.models["reid"] else None
        self.demographics = (
            DemographicsAnalyzer() if self.models["demographics"] else None
        )
        self.heatmap_generator = (
            HeatmapGenerator() if self.models["heatmap"] else None
        )
        self.zone_analytics = (
            ZoneAnalytics(camera_id) if self.models["zones"] else None
        )
        self.dwell_tracker = DwellTracker(camera_id)
        self.customer_session = CustomerSessionTracker(camera_id)
        self.queue_analytics = QueueAnalytics()
        self.customer_journey = CustomerJourney()

    # =====================================================
    # MAIN
    # =====================================================

    def process(self, frame):
        cam = self.camera_id
        self.frame_idx += 1

        frame = cv2.resize(frame, (1280, 720))

        if self.zone_analytics:
            self.zone_analytics.reset_counts()

        # ---- tracking ----
        tracked_objects = self.tracker.track(frame)
        analytics_service.update_tracking_metrics(tracked_objects, camera_id=cam)

        # ---- main per-object loop (reid + zone + queue + journey + draw) ----
        reid_map = {}
        for obj in tracked_objects:
            track_id = obj["track_id"]
            bbox = obj["bbox"]
            centroid = get_centroid(bbox)

            # identity
            if self.reid_manager:
                reid_id = self.reid_manager.match_identity(frame, bbox, cam)
                if reid_id is None:
                    continue
            else:
                reid_id = track_id
            reid_map[track_id] = reid_id

            # queue
            self.queue_analytics.update(reid_id, centroid)

            # zones (polygon locate -> id + name)
            zinfo = self.zone_analytics.locate(centroid) if self.zone_analytics else None
            zone_name = zinfo["name"] if zinfo else "Unknown"
            zone_id = zinfo["id"] if zinfo else None
            if zinfo:
                self.zone_analytics.zone_counts[zone_name] = \
                    self.zone_analytics.zone_counts.get(zone_name, 0) + 1

            # per-zone dwell (persists ZoneVisit on transitions)
            dwell = self.dwell_tracker.update(reid_id, zone_id, zone_name)

            # journey
            self.customer_journey.update(reid_id, zone_name)

            # movement persistence (legacy + new schema)
            analytics_service.log_movement(track_id, centroid, camera_id=cam)
            db_writer.enqueue(MovementPoint(
                camera_id=cam, customer_id=reid_id,
                x=float(centroid[0]), y=float(centroid[1]),
            ))

            # trajectory (namespaced so cameras don't collide track ids)
            traj_key = f"{cam}:{track_id}"
            update_trajectory(traj_key, centroid)

            # NOTE: live heatmap accumulation removed — the Heatmaps page
            # renders density from persisted MovementPoint data instead.

            # ---- rich per-person overlay ----
            # "#154 Male 25-34 Electronics 03:45"
            draw_tracking_box(frame, f"#{reid_id}", bbox)
            prof = analytics_service.customer_profiles.get(reid_id, {})
            # open/refresh a persistent customer visit
            self.customer_session.touch(reid_id, prof)
            demo = ""
            if prof:
                demo = f" {prof.get('gender', '')} {prof.get('age', '')}"
            mm, ss = divmod(int(dwell), 60)
            label = f"#{reid_id}{demo} | {zone_name} {mm:02d}:{ss:02d}"
            cv2.putText(
                frame, label, (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2,
            )
            draw_centroid(frame, centroid)
            draw_trajectory(frame, traj_key)

        # close zone + customer visits for customers who left the frame
        present_ids = set(reid_map.values())
        self.dwell_tracker.flush_stale(present_ids)
        self.customer_session.flush_stale(present_ids)

        # ---- demographics (throttled) ----
        if self.demographics:
            if self.frame_idx % self.demo_interval == 0:
                results = []
                for obj in tracked_objects:
                    res = self.demographics.analyze_person(
                        frame, obj["bbox"], obj["track_id"]
                    )
                    if res:
                        res["reid_id"] = reid_map.get(obj["track_id"])
                        results.append(res)
                        analytics_service.update_customer_profile(res)
                        if res.get("reid_id") is not None:
                            db_writer.enqueue(DemographicSample(
                                customer_id=res["reid_id"], camera_id=cam,
                                age=res.get("age"), gender=res.get("gender"),
                            ))
                self._cached_demographics = results
                analytics_service.update_demographics(results, camera_id=cam)
            self._draw_demographics(frame, self._cached_demographics)

        # ---- aggregate camera metrics ----
        analytics_service.update_queue_metrics(
            self.queue_analytics.queue_length,
            self.queue_analytics.average_wait,
            self.queue_analytics.get_status(),
            camera_id=cam,
        )
        if self.zone_analytics:
            analytics_service.update_zone_data(
                self.zone_analytics.zone_counts, camera_id=cam
            )
        if self.reid_manager:
            analytics_service.set_reid_identities(
                self.reid_manager.total_identities(), camera_id=cam
            )
            analytics_service.update_cross_camera(
                self.reid_manager.total_identities(), camera_id=cam
            )
            analytics_service.update_multi_camera_metrics(
                self.reid_manager.total_multi_camera_customers(), camera_id=cam
            )
        analytics_service.update_journey_metrics(
            self.customer_journey.total_customers(), camera_id=cam
        )

        # ---- overlays ----
        # NOTE: the heatmap density is intentionally NOT drawn on the live
        # annotated frame — it lives on the dedicated Heatmaps page (rendered
        # client-side from MovementPoint data). Live feeds stay clean.
        if self.zone_analytics:
            frame = self.zone_analytics.draw_zones(frame)
        frame = self.queue_analytics.draw_queue_zone(frame)
        self._draw_dashboard(frame)

        # ---- cleanup stale identities ----
        if self.reid_manager:
            self.reid_manager.cleanup()

        return frame

    # =====================================================
    # OVERLAY HELPERS
    # =====================================================

    def _draw_demographics(self, frame, results):
        for r in results:
            x, y, w, h = r["bbox"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
            cv2.putText(
                frame,
                f"#{r.get('reid_id', '?')} | {r['gender']} | {r['age']}",
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2,
            )

    def _draw_dashboard(self, frame):
        m = analytics_service.get_camera_metrics(self.camera_id)
        rows = [
            (f"Cam {self.camera_id}  Occ:{m['occupancy']}", (0, 255, 0)),
            (f"Entries:{m['entries']}  Tracks:{m['total_tracks']}", (255, 255, 0)),
            (f"ReID:{m['reid_identities']}  Multi:{m['multi_camera_customers']}", (0, 165, 255)),
            (f"M:{m['male_count']} F:{m['female_count']}  Q:{m['queue_length']}", (255, 0, 255)),
        ]
        y = 36
        for text, color in rows:
            cv2.putText(frame, text, (24, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            y += 34
