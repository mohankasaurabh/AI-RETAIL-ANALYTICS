from flask import Blueprint
from flask import jsonify

from backend.services.analytics_service import (
    analytics_service
)

from backend.database.queries import (
    DatabaseManager
)

# =====================================
# DATABASE
# =====================================

db_manager = DatabaseManager()

# =====================================
# BLUEPRINT
# =====================================

analytics_bp = Blueprint(

    "analytics",

    __name__
)

# =====================================
# LIVE DASHBOARD METRICS
# =====================================

@analytics_bp.route("/analytics")
def analytics():

    data = (
        analytics_service
        .get_dashboard_metrics()
    )

    return jsonify(data)

# =====================================
# LIVE CHART DATA
# =====================================

@analytics_bp.route("/chart_data")
def chart_data():

    data = (
        analytics_service
        .get_chart_data()
    )

    return jsonify(data)

# =====================================
# HISTORICAL DATABASE DATA
# =====================================

@analytics_bp.route("/historical_data")
def historical_data():

    try:

        data = (
            db_manager
            .get_occupancy_history()
        )

        return jsonify(data)

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500

# =====================================
# ZONE ANALYTICS
# =====================================

@analytics_bp.route("/zone_data")
def zone_data():

    metrics = (
        analytics_service
        .get_dashboard_metrics()
    )

    return jsonify(

        metrics.get(
            "zone_data",
            {}
        )
    )

# =====================================
# QUEUE ANALYTICS
# =====================================

@analytics_bp.route("/queue_data")
def queue_data():

    metrics = (
        analytics_service
        .get_dashboard_metrics()
    )

    return jsonify({

        "queue_length":
            metrics.get(
                "queue_length",
                0
            ),

        "average_wait":
            metrics.get(
                "average_wait",
                0
            ),

        "queue_status":
            metrics.get(
                "queue_status",
                "LOW"
            )
    })

# =====================================
# JOURNEY ANALYTICS
# =====================================

@analytics_bp.route("/journey_data")
def journey_data():

    metrics = (
        analytics_service
        .get_dashboard_metrics()
    )

    return jsonify({

        "journey_customers":
            metrics.get(
                "journey_customers",
                0
            )
    })

# =====================================
# SYSTEM HEALTH
# =====================================

@analytics_bp.route("/system_status")
def system_status():

    metrics = (
        analytics_service
        .get_dashboard_metrics()
    )

    return jsonify({

        "status":
            "running",

        "occupancy":
            metrics.get(
                "occupancy",
                0
            ),

        "tracks":
            metrics.get(
                "total_tracks",
                0
            ),

        "reid":
            metrics.get(
                "reid_identities",
                0
            )
    })