"""
=====================================================
Customer Routes — list, detail, demographics, returning
=====================================================
"""

from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify

from backend.database import repository


customer_bp = Blueprint("customers", __name__)

RANGE_DELTAS = {
    "today": None,  # special-cased
    "yesterday": None,
    "week": timedelta(days=7),
    "month": timedelta(days=30),
}


def _range(key):
    now = datetime.utcnow()
    if key == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0), None
    if key == "yesterday":
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, start + timedelta(days=1)
    if key in ("week", "month"):
        return now - RANGE_DELTAS[key], None
    return None, None  # all


@customer_bp.route("/api/customers")
def list_customers():
    start, end = _range(request.args.get("range", "all"))
    camera = request.args.get("camera")
    camera_id = int(camera) if camera and camera.isdigit() else None
    return jsonify(repository.list_customers(start, end, camera_id))


@customer_bp.route("/api/customers/demographics")
def demographics():
    start, end = _range(request.args.get("range", "all"))
    return jsonify(repository.customer_demographics(start, end))


@customer_bp.route("/api/customers/returning")
def returning():
    start, end = _range(request.args.get("range", "all"))
    return jsonify(repository.returning_customers(start, end))


@customer_bp.route("/api/customers/<int:customer_id>")
def detail(customer_id):
    d = repository.get_customer_detail(customer_id)
    if not d:
        return jsonify({"success": False, "message": "not found"}), 404
    return jsonify(d)
