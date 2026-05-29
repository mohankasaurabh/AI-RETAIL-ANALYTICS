from flask import Blueprint
from flask import jsonify


api_bp = Blueprint(
    "api",
    __name__
)


@api_bp.route("/api/status")
def api_status():

    return jsonify({
        "status": "running",
        "system": "AI Retail Analytics"
    })