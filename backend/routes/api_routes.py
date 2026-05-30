"""
=====================================================
Core API routes — status, stores, alerts
=====================================================
"""

from flask import Blueprint, jsonify, request

from backend.database import repository


api_bp = Blueprint("api", __name__)


@api_bp.route("/api/status")
def api_status():
    return jsonify({
        "status": "running",
        "system": "AI Retail Analytics",
    })


# =====================================
# STORES (single-tenant today)
# =====================================

@api_bp.route("/api/stores")
def api_stores():
    stores = repository.list_stores()
    if not stores:
        stores = [{"id": 1, "name": "Default Store", "location": ""}]
    return jsonify(stores)


# =====================================
# ALERTS
# =====================================

@api_bp.route("/api/alerts")
def api_alerts():
    only_unack = request.args.get("unack", "0") == "1"
    return jsonify(repository.list_alerts(limit=50, only_unack=only_unack))


@api_bp.route("/api/alerts/<int:alert_id>/ack", methods=["POST"])
def api_ack_alert(alert_id):
    ok = repository.ack_alert(alert_id)
    return jsonify({"success": ok})
