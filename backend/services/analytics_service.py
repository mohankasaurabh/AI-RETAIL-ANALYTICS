import time

from backend.database.queries import (
    DatabaseManager
)


class AnalyticsService:

    def __init__(self):

        # =====================================
        # LIVE METRICS
        # =====================================

        self.metrics = {

            "occupancy": 0,

            "entries": 0,

            "exits": 0,

            "active_customers": 0,

            "zone_occupancy": 0,

            "total_tracks": 0,

            "reid_identities": 0,

            "male_count": 0,

            "female_count": 0,

            "journey_customers": 0,

            "queue_length": 0,

            "average_wait": 0,

            "queue_status": "LOW",

            "cross_camera_customers": 0,

            "multi_camera_customers": 0,

            "zone_data": {}
        }

        # =====================================
        # CHART HISTORY
        # =====================================

        self.history = {

            "timestamps": [],

            "occupancy": [],

            "entries": [],

            "zone_occupancy": []
        }

        # =====================================
        # TRACK MEMORY
        # =====================================

        self.seen_track_ids = set()

        # =====================================
        # CUSTOMER PROFILES
        # =====================================

        self.customer_profiles = {}

        # =====================================
        # DATABASE
        # =====================================

        self.db_manager = DatabaseManager()

        self.last_save_time = time.time()

        self.save_interval = 5

    # =====================================
    # TRACKING METRICS
    # =====================================

    def update_tracking_metrics(
        self,
        tracked_objects
    ):

        current_track_ids = set()

        for obj in tracked_objects:

            track_id = obj["track_id"]

            current_track_ids.add(
                track_id
            )

            if (
                track_id
                not in
                self.seen_track_ids
            ):

                self.seen_track_ids.add(
                    track_id
                )

                self.metrics["entries"] += 1

        self.metrics["occupancy"] = len(
            current_track_ids
        )

        self.metrics["active_customers"] = len(
            current_track_ids
        )

        self.metrics["total_tracks"] = len(
            self.seen_track_ids
        )

        self.store_history()

        self.auto_save_analytics()

    # =====================================
    # AUTO DATABASE SAVE
    # =====================================

    def auto_save_analytics(self):

        current_time = time.time()

        if (

            current_time
            -
            self.last_save_time

            >=

            self.save_interval
        ):

            self.db_manager.save_analytics(
                self.metrics
            )

            print(
                "[INFO] Analytics Saved To Database"
            )

            self.last_save_time = current_time

    # =====================================
    # MOVEMENT LOGGING
    # =====================================

    def log_movement(
        self,
        track_id,
        centroid
    ):

        self.db_manager.save_movement(

            track_id,

            centroid
        )

    # =====================================
    # HISTORY
    # =====================================

    def store_history(self):

        timestamp = time.strftime(
            "%H:%M:%S"
        )

        self.history["timestamps"].append(
            timestamp
        )

        self.history["occupancy"].append(
            self.metrics["occupancy"]
        )

        self.history["entries"].append(
            self.metrics["entries"]
        )

        self.history["zone_occupancy"].append(
            self.metrics["zone_occupancy"]
        )

        if len(
            self.history["timestamps"]
        ) > 30:

            for key in self.history:

                self.history[key].pop(0)

    # =====================================
    # ZONE ANALYTICS
    # =====================================

    def update_zone_data(
        self,
        zone_counts
    ):

        self.metrics["zone_data"] = (
            zone_counts
        )

        self.metrics[
            "zone_occupancy"
        ] = sum(
            zone_counts.values()
        )

    # =====================================
    # REID
    # =====================================

    def set_reid_identities(
        self,
        count
    ):

        self.metrics[
            "reid_identities"
        ] = count

    # =====================================
    # DEMOGRAPHICS
    # =====================================

    def update_demographics(
        self,
        demographic_results
    ):

        male = 0

        female = 0

        for result in demographic_results:

            gender = result["gender"]

            if gender == "Man":

                male += 1

            else:

                female += 1

        self.metrics[
            "male_count"
        ] = male

        self.metrics[
            "female_count"
        ] = female

    # =====================================
    # CUSTOMER PROFILE
    # =====================================

    def update_customer_profile(
        self,
        demographic_result
    ):

        if demographic_result is None:

            return

        track_id = (
            demographic_result[
                "track_id"
            ]
        )

        self.customer_profiles[
            track_id
        ] = {

            "age":
                demographic_result["age"],

            "gender":
                demographic_result["gender"]
        }

    # =====================================
    # CUSTOMER JOURNEY
    # =====================================

    def update_journey_metrics(
        self,
        total_customers
    ):

        self.metrics[
            "journey_customers"
        ] = total_customers

    # =====================================
    # QUEUE ANALYTICS
    # =====================================

    def update_queue_metrics(
        self,
        queue_length,
        average_wait,
        status
    ):

        self.metrics[
            "queue_length"
        ] = queue_length

        self.metrics[
            "average_wait"
        ] = round(
            average_wait,
            1
        )

        self.metrics[
            "queue_status"
        ] = status

    # =====================================
    # CROSS CAMERA ANALYTICS
    # =====================================

    def update_cross_camera(
        self,
        count
    ):

        self.metrics[
            "cross_camera_customers"
        ] = count

    # =====================================
    # MULTI CAMERA ANALYTICS
    # =====================================

    def update_multi_camera_metrics(
        self,
        count
    ):

        self.metrics[
            "multi_camera_customers"
        ] = count

    # =====================================
    # DASHBOARD DATA
    # =====================================

    def get_dashboard_metrics(
        self
    ):

        return self.metrics

    # =====================================
    # CHART DATA
    # =====================================

    def get_chart_data(
        self
    ):

        return self.history


# =====================================
# GLOBAL ANALYTICS SERVICE
# =====================================

analytics_service = AnalyticsService()