"""
=====================================================
AI Retail Analytics Platform - Entry Point
=====================================================

Boots the Flask + Socket.IO server. Use socketio.run so
that real-time websocket events are served alongside the
HTTP routes and the MJPEG video stream.
"""

from app import create_app, socketio


app = create_app()


if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )
