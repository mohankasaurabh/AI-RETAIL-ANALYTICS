"""
=====================================================
Real-Time WebSocket Events (Flask-SocketIO)
=====================================================

Pushes live KPI metrics and chart history to every
connected dashboard client. A single background task
broadcasts the current state of the global
``analytics_service`` on a fixed interval, so all pages
(dashboard, live stream, analytics, heatmaps) receive the
same real-time stream without each client polling.

Emitted events
--------------
- ``metrics`` : full KPI dict (occupancy, entries, demographics, queue, zones...)
- ``chart``   : rolling time-series history for live charts
"""

from backend.services.analytics_service import analytics_service
from backend.services.alert_service import alert_service


# guard so the broadcast loop is started only once
_broadcaster_started = False

# how often (seconds) to push live metrics to clients
BROADCAST_INTERVAL = 1.0


def register_socket_events(socketio):

    print("[INFO] WebSocket Events Loaded")

    def _broadcast_loop():
        """Background task: push live metrics + chart history."""
        while True:
            try:
                socketio.emit(
                    "metrics",
                    analytics_service.get_dashboard_metrics()
                )
                socketio.emit(
                    "chart",
                    analytics_service.get_chart_data()
                )
                # threshold-based alerting (occupancy / queue)
                alert_service.evaluate(analytics_service)
            except Exception as exc:  # never let the loop die
                print(f"[SOCKET BROADCAST ERROR] {exc}")

            socketio.sleep(BROADCAST_INTERVAL)

    def _ensure_broadcaster():
        global _broadcaster_started
        if not _broadcaster_started:
            _broadcaster_started = True
            socketio.start_background_task(_broadcast_loop)

    # =====================================
    # CLIENT CONNECTED
    # =====================================

    @socketio.on("connect")
    def handle_connect():
        print("[SOCKET] Client connected")
        _ensure_broadcaster()
        # send an immediate snapshot so the UI is not blank
        socketio.emit(
            "metrics",
            analytics_service.get_dashboard_metrics()
        )
        socketio.emit(
            "chart",
            analytics_service.get_chart_data()
        )

    # =====================================
    # CLIENT DISCONNECTED
    # =====================================

    @socketio.on("disconnect")
    def handle_disconnect():
        print("[SOCKET] Client disconnected")

    # =====================================
    # EXPLICIT REFRESH REQUEST
    # =====================================

    @socketio.on("request_metrics")
    def handle_request_metrics():
        socketio.emit(
            "metrics",
            analytics_service.get_dashboard_metrics()
        )
