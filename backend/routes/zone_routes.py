"""
=====================================================
Zone Routes — CRUD + metrics + journey analytics
=====================================================
"""

from flask import Blueprint, request, jsonify

from backend.database import repository
from backend.services.analytics_service import analytics_service


zone_bp = Blueprint("zones", __name__)


# =====================================
# CRUD
# =====================================

@zone_bp.route("/api/cameras/<int:camera_id>/zones", methods=["GET"])
def list_zones(camera_id):
    zones = repository.list_zones(camera_id)
    # attach live occupancy from per-camera metrics
    live = analytics_service.get_camera_metrics(camera_id).get("zone_data", {})
    for z in zones:
        z["live_count"] = live.get(z["name"], 0)
    return jsonify(zones)


@zone_bp.route("/api/cameras/<int:camera_id>/zones", methods=["POST"])
def create_zone(camera_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("name") or len(data.get("points", [])) < 3:
        return jsonify({"success": False, "message": "name and >=3 points required"}), 400
    z = repository.create_zone(camera_id, data)
    return jsonify({"success": True, "zone": z})


@zone_bp.route("/api/zones/<int:zone_id>", methods=["PUT"])
def update_zone(zone_id):
    data = request.get_json(force=True, silent=True) or {}
    z = repository.update_zone(zone_id, data)
    if not z:
        return jsonify({"success": False, "message": "not found"}), 404
    return jsonify({"success": True, "zone": z})


@zone_bp.route("/api/zones/<int:zone_id>", methods=["DELETE"])
def delete_zone(zone_id):
    ok = repository.delete_zone(zone_id)
    return jsonify({"success": ok})


# =====================================
# ANALYTICS
# =====================================

@zone_bp.route("/api/cameras/<int:camera_id>/zones/metrics")
def zone_metrics(camera_id):
    return jsonify({
        "zones": repository.zone_metrics(camera_id),
        "hourly": repository.zone_hourly_activity(camera_id),
        "live": analytics_service.get_camera_metrics(camera_id).get("zone_data", {}),
    })


@zone_bp.route("/api/cameras/<int:camera_id>/zones/journey")
def zone_journey(camera_id):
    return jsonify(repository.zone_journeys(camera_id))
