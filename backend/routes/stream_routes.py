from flask import (
    Blueprint,
    Response,
    jsonify,
    request
)

import cv2
import time
import traceback

from ai_engine.stream.camera_manager import (
    camera_manager
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
# FRAME PROCESSOR
# =====================================

frame_processor = FrameProcessor()

# =====================================
# FRAME GENERATOR
# =====================================

def generate_frames():

    while True:

        try:

            frame = camera_manager.get_frame()

            if frame is None:

                time.sleep(0.1)

                continue

            processed_frame = (

                frame_processor.process_frame(

                    frame,

                    camera_manager.current_camera
                )
            )

            if processed_frame is None:

                continue

            ret, buffer = cv2.imencode(

                ".jpg",

                processed_frame
            )

            if not ret:

                continue

            frame_bytes = buffer.tobytes()

            yield (

                b"--frame\r\n"

                b"Content-Type: image/jpeg\r\n\r\n"

                +

                frame_bytes

                +

                b"\r\n"
            )

        except Exception as e:

            print(
                f"[STREAM ERROR] {e}"
            )

            traceback.print_exc()

            time.sleep(0.1)

            continue

# =====================================
# VIDEO FEED
# =====================================

@stream_bp.route("/video_feed")
def video_feed():

    return Response(

        generate_frames(),

        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
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

    if not camera_id:

        return jsonify({

            "success": False,

            "message":
                "Camera ID missing"
        })

    success = (

        camera_manager.switch_camera(
            camera_id
        )
    )

    return jsonify({

        "success": success,

        "camera":
            camera_manager.current_camera
    })

# =====================================
# CONNECT RTSP
# =====================================

@stream_bp.route(
    "/connect_rtsp",
    methods=["POST"]
)
def connect_rtsp():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Missing request body"
            })

        rtsp_url = data.get(
            "rtsp_url",
            ""
        ).strip()

        if not rtsp_url.startswith(
            "rtsp://"
        ):

            return jsonify({

                "success": False,

                "message":
                    "Invalid RTSP URL"
            })

        camera_manager.set_rtsp_url(
            rtsp_url
        )

        success = (

            camera_manager.switch_camera(
                "rtsp"
            )
        )

        return jsonify({

            "success": success,

            "camera": "rtsp"
        })

    except Exception as e:

        traceback.print_exc()

        return jsonify({

            "success": False,

            "message": str(e)
        })

# =====================================
# PAUSE STREAM
# =====================================

@stream_bp.route("/pause_stream")
def pause_stream():

    camera_manager.pause()

    return jsonify({

        "success": True,

        "status": "paused"
    })

# =====================================
# PLAY STREAM
# =====================================

@stream_bp.route("/play_stream")
def play_stream():

    camera_manager.play()

    return jsonify({

        "success": True,

        "status": "playing"
    })

# =====================================
# RESTART STREAM
# =====================================

@stream_bp.route("/restart_stream")
def restart_stream():

    success = (

        camera_manager.restart_camera()
    )

    return jsonify({

        "success": success,

        "camera":
            camera_manager.current_camera
    })

# =====================================
# CAMERA STATUS
# =====================================

@stream_bp.route("/camera_status")
def camera_status():

    return jsonify({

        "camera":
            camera_manager.current_camera,

        "paused":
            camera_manager.paused
    })