from backend.database.db import (
    SessionLocal
)

from datetime import datetime, timedelta

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

    # =========================
    # MOVEMENT POINTS (heatmap)
    # =========================

    def get_movement_points(
        self,
        limit=2000
    ):
        """Return recent (x, y) movement points for heatmaps."""

        logs = self.db.query(
            MovementLog
        ).order_by(
            MovementLog.timestamp.desc()
        ).limit(limit).all()

        return [
            {"x": log.x, "y": log.y}
            for log in logs
        ]

    # =========================
    # HOURLY FOOTFALL
    # =========================

    def get_hourly_footfall(self):
        """Aggregate entries/occupancy into 24 hourly buckets."""

        hours = [0] * 24
        occ = [0] * 24
        counts = [0] * 24

        logs = self.db.query(AnalyticsLog).all()

        prev_entries = 0

        for log in logs:
            h = log.timestamp.hour
            # entries is a running counter -> take positive deltas
            delta = max(0, (log.entries or 0) - prev_entries)
            prev_entries = log.entries or prev_entries
            hours[h] += delta
            occ[h] += (log.occupancy or 0)
            counts[h] += 1

        avg_occ = [
            round(occ[i] / counts[i], 1) if counts[i] else 0
            for i in range(24)
        ]

        return {
            "labels": [f"{h:02d}:00" for h in range(24)],
            "entries": hours,
            "avg_occupancy": avg_occ
        }

    # =========================
    # ANALYTICS IN DATE RANGE
    # =========================

    def get_analytics_in_range(
        self,
        start=None,
        end=None,
        limit=5000
    ):
        """Fetch analytics rows within an optional datetime range."""

        query = self.db.query(AnalyticsLog)

        if start is not None:
            query = query.filter(
                AnalyticsLog.timestamp >= start
            )

        if end is not None:
            query = query.filter(
                AnalyticsLog.timestamp <= end
            )

        logs = query.order_by(
            AnalyticsLog.timestamp.asc()
        ).limit(limit).all()

        results = []

        for log in logs:
            results.append({
                "timestamp": log.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "occupancy": log.occupancy,
                "entries": log.entries,
                "exits": log.exits,
                "active_customers": log.active_customers,
                "zone_occupancy": log.zone_occupancy,
                "total_tracks": log.total_tracks,
                "reid_identities": log.reid_identities
            })

        return results

    # =========================
    # DATE RANGE HELPER
    # =========================

    @staticmethod
    def resolve_range(range_key, now=None):
        """Map a filter key (today/yesterday/week/month) to a
        (start, end) datetime tuple. Returns (None, None) for 'all'."""

        now = now or datetime.utcnow()
        today = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if range_key == "today":
            return today, now

        if range_key == "yesterday":
            return today - timedelta(days=1), today

        if range_key == "week":
            return today - timedelta(days=7), now

        if range_key == "month":
            return today - timedelta(days=30), now

        return None, None