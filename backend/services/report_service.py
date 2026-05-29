import pandas as pd

from backend.database.queries import (
    DatabaseManager
)


class ReportService:

    def __init__(self):

        self.db_manager = DatabaseManager()

    # =========================
    # EXPORT ANALYTICS CSV
    # =========================

    def export_analytics_csv(self):

        logs = self.db_manager.get_occupancy_history(
            limit=500
        )

        df = pd.DataFrame(logs)

        export_path = (
            "data/exports/"
            "analytics_report.csv"
        )

        df.to_csv(
            export_path,
            index=False
        )

        return export_path