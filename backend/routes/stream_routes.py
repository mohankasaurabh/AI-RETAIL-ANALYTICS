import cv2

from flask import Blueprint
from flask import Response
from flask import request
from flask import jsonify

from ai_engine.stream.camera_manager import (
    CameraManager
)

from ai_engine.stream.frame_processor import (
    FrameProcessor
)


# =====================================
# BLUEPRINT
# =====================================

stream_bp = Blueprint(
    "stream",
    __name__
)


# =====================================
# COMPONENTS
# =====================================

camera_manager = CameraManager()

frame_processor = FrameProcessor()


# =====================================
# FRAME GENERATOR
# =====================================

def generate_frames():

    while True:

        frame = camera_manager.get_frame()

        if frame is None:

            continue

        # =====================================
        # UNIFIED AI PIPELINE
        # =====================================

        processed_frame = (
            frame_processor.process_frame(

                frame,

                camera_manager.current_camera
            )
        )

        # Encode frame
        _, buffer = cv2.imencode(

            ".jpg",

            processed_frame
        )

        frame_bytes = buffer.tobytes()

        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + frame_bytes +

            b"\r\n"
        )


# =====================================
# VIDEO STREAM
# =====================================

@stream_bp.route("/video_feed")
def video_feed():

    return Response(

        generate_frames(),

        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )
    )


# =====================================
# SWITCH CAMERA
# =====================================

@stream_bp.route("/switch_camera")
def switch_camera():

    camera_id = request.args.get(
        "camera"
    )

    success = camera_manager.switch_camera(
        camera_id
    )

    return jsonify({

        "success": success,

        "camera": camera_id
    })


# =====================================
# PAUSE STREAM
# =====================================

@stream_bp.route("/pause_stream")
def pause_stream():

    camera_manager.pause()

    return jsonify({

        "status": "paused"
    })


# =====================================
# PLAY STREAM
# =====================================

@stream_bp.route("/play_stream")
def play_stream():

    camera_manager.play()

    return jsonify({

        "status": "playing"
    })


# =====================================
# RESTART STREAM
# =====================================

@stream_bp.route("/restart_stream")
def restart_stream():

    camera_manager.restart_camera()

    return jsonify({

        "status": "restarted"
    })


# =====================================
# CAMERA STATUS
# =====================================

@stream_bp.route("/camera_status")
def camera_status():

    return jsonify({

        "current_camera":
            camera_manager.current_camera,

        "paused":
            camera_manager.paused,

        "available_cameras":
            list(
                camera_manager.sources.keys()
            )
    })


@stream_bp.route(
    "/connect_rtsp",
    methods=["POST"]
)
def connect_rtsp():

    data = request.json

    rtsp_url = data.get(
        "rtsp_url"
    )

    camera_manager.sources[
        "rtsp"
    ]["path"] = rtsp_url

    success = camera_manager.switch_camera(
        "rtsp"
    )

    return jsonify({

        "success": success,

        "camera": "rtsp"
    })


