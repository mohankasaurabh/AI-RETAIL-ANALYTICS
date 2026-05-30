"""
=====================================================
Report Routes
=====================================================

/export_report            -> legacy CSV (kept working)
/export/<fmt>?range=<key> -> CSV / Excel / PDF with filters

fmt   : csv | excel | pdf
range : today | yesterday | week | month | all
"""

from flask import Blueprint, request, send_file, jsonify

from backend.services.report_service import ReportService


report_bp = Blueprint("reports", __name__)

report_service = ReportService()


# =====================================
# LEGACY CSV EXPORT (back-compat)
# =====================================

@report_bp.route("/export_report")
def export_report():
    report_path = report_service.export_analytics_csv()
    return send_file(report_path, as_attachment=True)


# =====================================
# FORMATTED EXPORT WITH FILTERS
# =====================================

@report_bp.route("/export/<fmt>")
def export(fmt):

    range_key = request.args.get("range", "all")

    try:
        path = report_service.generate(fmt=fmt, range_key=range_key)
        return send_file(path, as_attachment=True)

    except Exception as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 500


# =====================================================
# RICH REPORTS (daily / weekly / monthly)
# =====================================================

@report_bp.route("/api/reports/summary")
def report_summary():
    rtype = request.args.get("type", "daily")
    try:
        return jsonify(report_service.summary(rtype))
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@report_bp.route("/api/reports/<rtype>")
def report_download(rtype):
    fmt = request.args.get("fmt", "pdf")
    if rtype not in ("daily", "weekly", "monthly"):
        return jsonify({"success": False, "message": "invalid report type"}), 400
    try:
        path = report_service.build(report_type=rtype, fmt=fmt)
        return send_file(path, as_attachment=True)
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
