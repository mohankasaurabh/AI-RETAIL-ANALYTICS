"""
=====================================================
Settings Routes
=====================================================
"""

from flask import Blueprint, request, jsonify

from backend.services import settings_service


settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(settings_service.get_all())


@settings_bp.route("/api/settings", methods=["PUT"])
def update_settings():
    data = request.get_json(force=True, silent=True) or {}
    return jsonify({"success": True, "settings": settings_service.save(data)})
