import cv2


class CameraManager:

    def __init__(self):

        # =====================================
        # AVAILABLE SOURCES
        # =====================================

        self.sources = {

            "mall": {

                "type": "video",

                "path": "data/videos/mall.mp4"
            },

            "webcam": {

                "type": "webcam",

                "path": 0
            },

            "rtsp": {

                "type": "rtsp",

                "path": ""
            }
        }

        # =====================================
        # DEFAULT CAMERA
        # =====================================

        self.current_camera = "mall"

        self.cap = None

        self.paused = False

        self.open_source(
            self.current_camera
        )

    # =====================================
    # OPEN SOURCE
    # =====================================

    def open_source(
        self,
        source_id
    ):

        if source_id not in self.sources:

            print(
                f"[ERROR] Unknown source: {source_id}"
            )

            return False

        source = self.sources[source_id]

        source_type = source["type"]

        source_path = source["path"]

        try:

            if source_type == "video":

                self.cap = cv2.VideoCapture(
                    source_path
                )

            elif source_type == "webcam":

                self.cap = cv2.VideoCapture(
                    source_path
                )

            elif source_type == "rtsp":

                self.cap = cv2.VideoCapture(
                    source_path
                )

                # Helps reduce RTSP buffering
                self.cap.set(
                    cv2.CAP_PROP_BUFFERSIZE,
                    1
                )

            else:

                print(
                    f"[ERROR] Unsupported source type: {source_type}"
                )

                return False

            if not self.cap.isOpened():

                print(
                    f"[ERROR] Cannot open source: {source_path}"
                )

                return False

            return True

        except Exception as e:

            print(
                f"[ERROR] Source open failed: {e}"
            )

            return False

    # =====================================
    # GET FRAME
    # =====================================

    def get_frame(self):

        if self.paused:

            return None

        if self.cap is None:

            return None

        ret, frame = self.cap.read()

        if not ret:

            # Loop video files
            source = self.sources[
                self.current_camera
            ]

            if source["type"] == "video":

                self.cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                ret, frame = self.cap.read()

                if not ret:

                    return None

            else:

                return None

        return frame

    # =====================================
    # SWITCH CAMERA
    # =====================================

    def switch_camera(
        self,
        camera_id
    ):

        if camera_id not in self.sources:

            return False

        try:

            if self.cap:

                self.cap.release()

            self.current_camera = camera_id

            return self.open_source(
                camera_id
            )

        except Exception as e:

            print(
                f"[ERROR] Camera switch failed: {e}"
            )

            return False

    # =====================================
    # UPDATE RTSP URL
    # =====================================

    def set_rtsp_url(
        self,
        rtsp_url
    ):

        self.sources["rtsp"]["path"] = rtsp_url

    # =====================================
    # PAUSE
    # =====================================

    def pause(self):

        self.paused = True

    # =====================================
    # PLAY
    # =====================================

    def play(self):

        self.paused = False

    # =====================================
    # RESTART
    # =====================================

    def restart_camera(self):

        self.switch_camera(
            self.current_camera
        )

    # =====================================
    # CLEANUP
    # =====================================

    def release(self):

        if self.cap:

            self.cap.release()