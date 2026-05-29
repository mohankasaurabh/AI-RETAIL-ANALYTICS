import cv2

from ai_engine.tracking.tracker import (
    CustomerTracker
)

from ai_engine.tracking.tracking_utils import (
    draw_tracking_box,
    draw_centroid,
    draw_trajectory,
    get_centroid,
    update_trajectory
)

from ai_engine.demographics.age_gender import (
    DemographicsAnalyzer
)

from ai_engine.analytics.heatmap_generator import (
    HeatmapGenerator
)

from ai_engine.analytics.zone_analytics import (
    ZoneAnalytics
)

from ai_engine.analytics.customer_journey import (
    CustomerJourney
)

from ai_engine.reid.reid_model import (
    ReIDManager
)

from backend.services.analytics_service import (
    analytics_service
)

from ai_engine.analytics.queue_analytics import (
    QueueAnalytics
)

class FrameProcessor:

    def __init__(self):

        # =====================================
        # CORE AI MODULES
        # =====================================

        self.tracker = CustomerTracker()

        self.demographics = (
            DemographicsAnalyzer()
        )

        self.heatmap_generator = (
            HeatmapGenerator()
        )

        self.zone_analytics = (
            ZoneAnalytics()
        )

        self.queue_analytics = (
            QueueAnalytics()
        )

        self.customer_journey = (
            CustomerJourney()
        )

        self.reid_manager = (
            ReIDManager()
        )

    # =====================================
    # MAIN UNIFIED AI PIPELINE
    # =====================================

    def process_frame(
        self,
        frame,
        current_camera
    ):

        # =====================================
        # FRAME PREPROCESSING
        # =====================================

        frame = cv2.resize(
            frame,
            (1280, 720)
        )

        # =====================================
        # RESET ZONE COUNTS
        # =====================================

        self.zone_analytics.reset_counts()

        # =====================================
        # TRACKING
        # =====================================

        tracked_objects = self.tracker.track(
            frame
        )

        # =====================================
        # UPDATE TRACKING METRICS
        # =====================================

        analytics_service.update_tracking_metrics(
            tracked_objects
        )

        # =====================================
        # DEMOGRAPHICS
        # =====================================

        demographic_results = []

        for obj in tracked_objects:

            track_id = obj["track_id"]

            bbox = obj["bbox"]

            result = (
                self.demographics.analyze_person(

                    frame,

                    bbox,

                    track_id
                )
            )

            if result:

                demographic_results.append(
                    result
                )

                analytics_service.update_customer_profile(
                    result
                )

        # =====================================
        # UPDATE DEMOGRAPHICS METRICS
        # =====================================

        analytics_service.update_demographics(
            demographic_results
        )

        # =====================================
        # MAIN TRACKING LOOP
        # =====================================

        for obj in tracked_objects:

            track_id = obj["track_id"]

            bbox = obj["bbox"]

            centroid = get_centroid(
                bbox
            )

            # =====================================
            # REID ASSOCIATION
            # =====================================

            reid_id = (
                self.reid_manager.match_identity(

                    frame,

                    bbox,
                    current_camera
                )
            )

            self.queue_analytics.update(

                reid_id,

                centroid
            )


            # =====================================
            # ZONE ANALYTICS
            # =====================================

            self.zone_analytics.update(
                centroid
            )

            current_zone = (
                self.zone_analytics.get_zone(
                    centroid
                )
            )

            # =====================================
            # CUSTOMER JOURNEY
            # =====================================

            self.customer_journey.update(

                reid_id,

                current_zone
            )

            # =====================================
            # DATABASE MOVEMENT LOGGING
            # =====================================

            analytics_service.log_movement(

                track_id,

                centroid
            )

            # =====================================
            # TRAJECTORY UPDATE
            # =====================================

            update_trajectory(

                track_id,

                centroid
            )

            # =====================================
            # HEATMAP UPDATE
            # =====================================

            self.heatmap_generator.update(
                centroid
            )

            # =====================================
            # DRAW TRACKING BOX
            # =====================================

            draw_tracking_box(

                frame,

                f"T{track_id} | R{reid_id}",

                bbox
            )

            # =====================================
            # JOURNEY INFO
            # =====================================

            journey = (
                self.customer_journey
                .get_journey(reid_id)
            )

            if journey:

                zone_text = (
                    f"Zone: "
                    f"{journey['current_zone']}"
                )

                cv2.putText(

                    frame,

                    zone_text,

                    (bbox[0], bbox[1] - 30),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    (0, 255, 255),

                    2
                )

            # =====================================
            # DRAW CENTROID
            # =====================================

            draw_centroid(

                frame,

                centroid
            )

            # =====================================
            # DRAW TRAJECTORY
            # =====================================

            draw_trajectory(

                frame,

                track_id
            )


        analytics_service.update_queue_metrics(

            self.queue_analytics.queue_length,

            self.queue_analytics.average_wait,

            self.queue_analytics.get_status()
        )


        # =====================================
        # UPDATE ZONE METRICSƒˇ
        # =====================================

        analytics_service.update_zone_data(

            self.zone_analytics.zone_counts
        )

        # =====================================
        # UPDATE REID METRICS
        # =====================================

        analytics_service.set_reid_identities(

            self.reid_manager.total_identities()
        )

        # =====================================
        # CROSS CAMERA REID METRICS
        # =====================================

        analytics_service.update_cross_camera(

            self.reid_manager.total_multi_camera_customers()
        )

        analytics_service.update_multi_camera_metrics(

            self.reid_manager.total_multi_camera_identities()
        )


        # =====================================
        # UPDATE JOURNEY METRICS
        # =====================================

        analytics_service.update_journey_metrics(

            self.customer_journey.total_customers()
        )

        # =====================================
        # DRAW DEMOGRAPHICS
        # =====================================

        for result in demographic_results:

            x, y, w, h = result["bbox"]

            age = result["age"]

            gender = result["gender"]

            track_id = result["track_id"]

            # Face rectangle
            cv2.rectangle(

                frame,

                (x, y),

                (x + w, y + h),

                (255, 0, 255),

                2
            )

            # Face analytics label
            cv2.putText(

                frame,

                f"ID {track_id} | "
                f"{gender} | "
                f"{age}",

                (x, y - 10),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 0, 255),

                2
            )

        # =====================================
        # HEATMAP OVERLAY
        # =====================================

        frame = (
            self.heatmap_generator
            .overlay_heatmap(frame)
        )

        # =====================================
        # DRAW ZONE ANALYTICS
        # =====================================

        frame = self.zone_analytics.draw_zones(
            frame
        )

        frame = self.queue_analytics.draw_queue_zone(
            frame
        )
        
        # =====================================
        # DASHBOARD OVERLAYS
        # =====================================

        metrics = (
            analytics_service
            .get_dashboard_metrics()
        )

        overlay_data = [

            (
                f"Occupancy: "
                f"{metrics['occupancy']}",

                (0, 255, 0)
            ),

            (
                f"Entries: "
                f"{metrics['entries']}",

                (255, 255, 0)
            ),

            (
                f"Tracks: "
                f"{metrics['total_tracks']}",

                (0, 200, 255)
            ),

            (
                f"ReID: "
                f"{metrics['reid_identities']}",

                (0, 165, 255)
            ),

            (
                f"Journeys: "
                f"{metrics['journey_customers']}",

                (255, 255, 255)
            ),

            (
                f"Male: "
                f"{metrics['male_count']}",

                (255, 100, 0)
            ),

            (
                f"Female: "
                f"{metrics['female_count']}",

                (255, 0, 255)
            ),

            (
                f"Camera: "
                f"{current_camera}",

                (0, 255, 255)
            ),

            (
                f"Queue: "
                f"{metrics['queue_length']}",

                (0, 0, 255)
            ),

            (
                f"Avg Wait: "
                f"{metrics['average_wait']:.1f}s",

                (255, 255, 255)
            ),

            (
                f"Queue Status: "
                f"{metrics['queue_status']}",

                (0, 0, 255)
            ),

            (
                f"Multi-Cam: "
                f"{metrics['multi_camera_customers']}",

                (255, 255, 0)
            )
        ]

        y = 40

        for text, color in overlay_data:

            cv2.putText(

                frame,

                text,

                (30, y),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                color,

                2
            )

            y += 40


        # =====================================
        # CLEANUP OLD IDENTITIES
        # =====================================

        self.reid_manager.cleanup()

        # =====================================
        # RETURN FINAL FRAME
        # =====================================

        return frame