"""
=====================================================
Report Service
=====================================================

Generates analytics reports in CSV / Excel / PDF formats
with optional date-range filtering (today / yesterday /
week / month / all). Files are written under data/exports/.

- CSV   : pandas
- Excel : pandas + openpyxl (styled header)
- PDF   : matplotlib (table + summary, no extra native deps)
"""

import os

from datetime import datetime, timedelta

import pandas as pd

import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt

from backend.database.queries import DatabaseManager
from backend.database import repository


EXPORT_DIR = "data/exports"

# report_type -> lookback window
REPORT_RANGES = {
    "daily": timedelta(days=1),
    "weekly": timedelta(days=7),
    "monthly": timedelta(days=30),
}


class ReportService:

    def __init__(self):
        self.db_manager = DatabaseManager()
        os.makedirs(EXPORT_DIR, exist_ok=True)

    # =========================
    # DATA LOADER
    # =========================

    def _load(self, range_key="all"):
        start, end = DatabaseManager.resolve_range(range_key)
        rows = self.db_manager.get_analytics_in_range(start, end)
        if not rows:
            # keep columns stable even when empty
            rows = [{
                "timestamp": "", "occupancy": 0, "entries": 0,
                "exits": 0, "active_customers": 0,
                "zone_occupancy": 0, "total_tracks": 0,
                "reid_identities": 0
            }]
        return pd.DataFrame(rows)

    # =========================
    # CSV
    # =========================

    def export_csv(self, range_key="all"):
        df = self._load(range_key)
        path = os.path.join(EXPORT_DIR, f"report_{range_key}.csv")
        df.to_csv(path, index=False)
        return path

    # backwards-compatible alias (used by legacy /export_report)
    def export_analytics_csv(self):
        return self.export_csv("all")

    # =========================
    # EXCEL
    # =========================

    def export_excel(self, range_key="all"):
        df = self._load(range_key)
        path = os.path.join(EXPORT_DIR, f"report_{range_key}.xlsx")

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Analytics")

            # lightweight summary sheet
            summary = pd.DataFrame([{
                "Total Records": len(df),
                "Peak Occupancy": int(df["occupancy"].max()),
                "Total Entries": int(df["entries"].max()),
                "Unique Tracks": int(df["total_tracks"].max()),
                "ReID Identities": int(df["reid_identities"].max())
            }])
            summary.to_excel(writer, index=False, sheet_name="Summary")

        return path

    # =========================
    # PDF
    # =========================

    def export_pdf(self, range_key="all"):
        df = self._load(range_key)
        path = os.path.join(EXPORT_DIR, f"report_{range_key}.pdf")

        # show only the most recent rows to keep the table readable
        view = df.tail(25)

        fig, (ax_title, ax_table) = plt.subplots(
            2, 1,
            figsize=(11, 8.5),
            gridspec_kw={"height_ratios": [1, 6]}
        )

        # header / summary block
        ax_title.axis("off")
        ax_title.text(
            0.5, 0.8,
            "AI Retail Analytics Report",
            ha="center", fontsize=20, fontweight="bold"
        )
        ax_title.text(
            0.5, 0.45,
            f"Range: {range_key.upper()}   |   Records: {len(df)}",
            ha="center", fontsize=11
        )
        ax_title.text(
            0.5, 0.15,
            (
                f"Peak Occupancy: {int(df['occupancy'].max())}   "
                f"Total Entries: {int(df['entries'].max())}   "
                f"ReID: {int(df['reid_identities'].max())}"
            ),
            ha="center", fontsize=10, color="#555"
        )

        # data table
        ax_table.axis("off")
        table = ax_table.table(
            cellText=view.values,
            colLabels=view.columns,
            loc="center",
            cellLoc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(7)
        table.scale(1, 1.3)

        # style header row
        for col in range(len(view.columns)):
            cell = table[0, col]
            cell.set_facecolor("#0f172a")
            cell.set_text_props(color="white", fontweight="bold")

        fig.tight_layout()
        fig.savefig(path, format="pdf")
        plt.close(fig)

        return path

    # =========================
    # DISPATCH
    # =========================

    def generate(self, fmt="csv", range_key="all"):
        fmt = (fmt or "csv").lower()
        if fmt == "excel" or fmt == "xlsx":
            return self.export_excel(range_key)
        if fmt == "pdf":
            return self.export_pdf(range_key)
        return self.export_csv(range_key)

    # =====================================================
    # RICH MULTI-SECTION REPORTS (new schema)
    # =====================================================

    def _gather(self, report_type="daily"):
        """Collect footfall / zones / demographics / summary for a window."""
        delta = REPORT_RANGES.get(report_type, REPORT_RANGES["daily"])
        start = datetime.utcnow() - delta

        footfall = repository.snapshots_in_range(start=start)

        zones = []
        for cam in repository.list_cameras():
            for z in repository.zone_metrics(cam["id"]):
                z["camera"] = cam["name"]
                zones.append(z)
        zones.sort(key=lambda r: r["total_visits"], reverse=True)

        demo = repository.customer_demographics(start=start)
        returning = repository.returning_customers(start=start)

        summary = {
            "report_type": report_type,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "window_start": start.strftime("%Y-%m-%d %H:%M:%S"),
            "peak_occupancy": max((f["occupancy"] for f in footfall), default=0),
            "total_entries": max((f["entries"] for f in footfall), default=0),
            "unique_customers": demo["total"],
            "returning_customers": returning["count"],
            "male": demo["male"],
            "female": demo["female"],
        }
        return {
            "summary": summary, "footfall": footfall,
            "zones": zones, "demographics": demo,
        }

    def summary(self, report_type="daily"):
        """JSON summary for the Reports page preview."""
        data = self._gather(report_type)
        return {
            "summary": data["summary"],
            "footfall": data["footfall"][-60:],
            "zones": data["zones"],
            "demographics": data["demographics"],
        }

    def build(self, report_type="daily", fmt="pdf"):
        fmt = (fmt or "pdf").lower()
        data = self._gather(report_type)
        base = os.path.join(EXPORT_DIR, f"report_{report_type}")
        if fmt in ("excel", "xlsx"):
            return self._build_excel(base + ".xlsx", data)
        if fmt == "csv":
            return self._build_csv(base + ".csv", data)
        return self._build_pdf(base + ".pdf", data, report_type)

    def _build_csv(self, path, data):
        df = pd.DataFrame(data["footfall"]) if data["footfall"] else pd.DataFrame(
            columns=["ts", "occupancy", "entries"])
        df.to_csv(path, index=False)
        return path

    def _build_excel(self, path, data):
        with pd.ExcelWriter(path, engine="openpyxl") as w:
            pd.DataFrame([data["summary"]]).to_excel(w, index=False, sheet_name="Summary")
            (pd.DataFrame(data["footfall"]) if data["footfall"]
             else pd.DataFrame(columns=["ts"])).to_excel(w, index=False, sheet_name="Footfall")
            (pd.DataFrame(data["zones"]) if data["zones"]
             else pd.DataFrame(columns=["name"])).to_excel(w, index=False, sheet_name="Zones")
            d = data["demographics"]
            pd.DataFrame({"age_group": d["age_labels"], "count": d["age_values"]}).to_excel(
                w, index=False, sheet_name="Demographics")
        return path

    def _build_pdf(self, path, data, report_type):
        s = data["summary"]
        fig = plt.figure(figsize=(11, 8.5))

        # title + summary
        ax0 = fig.add_axes([0.05, 0.82, 0.9, 0.15]); ax0.axis("off")
        ax0.text(0.5, 0.8, f"AI Retail — {report_type.title()} Report",
                 ha="center", fontsize=20, fontweight="bold")
        ax0.text(0.5, 0.35, (
            f"Generated {s['generated_at']}   |   Peak Occupancy {s['peak_occupancy']}   |   "
            f"Entries {s['total_entries']}   |   Unique {s['unique_customers']}   |   "
            f"Returning {s['returning_customers']}"), ha="center", fontsize=10, color="#555")

        # footfall line
        ax1 = fig.add_axes([0.08, 0.50, 0.5, 0.26])
        ff = data["footfall"]
        if ff:
            ax1.plot([f["occupancy"] for f in ff], color="#2563eb")
        ax1.set_title("Occupancy over time", fontsize=11)
        ax1.tick_params(labelsize=7)

        # gender pie
        ax2 = fig.add_axes([0.66, 0.50, 0.28, 0.26])
        if s["male"] or s["female"]:
            ax2.pie([s["male"], s["female"]], labels=["Male", "Female"],
                    autopct="%1.0f%%", colors=["#38bdf8", "#f472b6"])
        else:
            ax2.text(0.5, 0.5, "No demographics", ha="center", fontsize=9, color="#888")
            ax2.axis("off")
        ax2.set_title("Gender", fontsize=11)

        # zone table
        ax3 = fig.add_axes([0.08, 0.06, 0.86, 0.36]); ax3.axis("off")
        ax3.set_title("Zone Performance", fontsize=11, loc="left")
        zrows = [[z["name"], z["total_visits"], z["unique_visitors"],
                  z["avg_dwell"], z["max_dwell"], z["revisits"]]
                 for z in data["zones"][:12]]
        if zrows:
            t = ax3.table(cellText=zrows,
                          colLabels=["Zone", "Visits", "Unique", "Avg Dwell", "Max Dwell", "Revisits"],
                          loc="upper center", cellLoc="center")
            t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.3)
            for c in range(6):
                t[0, c].set_facecolor("#0f172a")
                t[0, c].set_text_props(color="white", fontweight="bold")
        else:
            ax3.text(0.5, 0.5, "No zone data", ha="center", fontsize=9, color="#888")

        fig.savefig(path, format="pdf")
        plt.close(fig)
        return path
