from flask import Blueprint
from flask import send_file

from backend.services.report_service import (
    ReportService
)


report_bp = Blueprint(
    "reports",
    __name__
)

report_service = ReportService()


@report_bp.route("/export_report")
def export_report():

    report_path = (
        report_service.export_analytics_csv()
    )

    return send_file(
        report_path,
        as_attachment=True
    )