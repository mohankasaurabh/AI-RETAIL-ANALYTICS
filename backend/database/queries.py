from backend.database.db import (
    SessionLocal
)

from backend.database.models import (
    AnalyticsLog,
    MovementLog
)


class DatabaseManager:

    def __init__(self):

        self.db = SessionLocal()

    # =========================
    # ANALYTICS LOGS
    # =========================

    def save_analytics(self, metrics):

        log = AnalyticsLog(

            occupancy=metrics["occupancy"],

            entries=metrics["entries"],

            exits=metrics["exits"],

            active_customers=
                metrics["active_customers"],

            zone_occupancy=
                metrics["zone_occupancy"],

            total_tracks=
                metrics["total_tracks"],

            reid_identities=
                metrics["reid_identities"]
        )

        self.db.add(log)

        self.db.commit()

    # =========================
    # MOVEMENT LOGS
    # =========================

    def save_movement(
        self,
        track_id,
        centroid
    ):

        x, y = centroid

        log = MovementLog(

            track_id=track_id,

            x=x,

            y=y
        )

        self.db.add(log)

        self.db.commit()

    # =========================
    # FETCH ANALYTICS
    # =========================

    def get_recent_analytics(
        self,
        limit=20
    ):

        return self.db.query(
            AnalyticsLog
        ).order_by(
            AnalyticsLog.timestamp.desc()
        ).limit(limit).all()
    

    # =========================
    # HISTORICAL ANALYTICS
    # =========================

    def get_occupancy_history(
        self,
        limit=50
    ):

        logs = self.db.query(
            AnalyticsLog
        ).order_by(
            AnalyticsLog.timestamp.asc()
        ).limit(limit).all()

        results = []

        for log in logs:

            results.append({

                "timestamp":
                    log.timestamp.strftime(
                        "%H:%M:%S"
                    ),

                "occupancy":
                    log.occupancy,

                "entries":
                    log.entries,

                "active_customers":
                    log.active_customers,

                "zone_occupancy":
                    log.zone_occupancy
            })

        return results