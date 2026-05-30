import cv2


class CameraManager:

    def __init__(self):

        # =====================================
        # CAMERA SOURCES
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
        # CURRENT SOURCE
        # =====================================

        self.current_camera = "mall"

        self.cap = None

        self.paused = False

        self.open_source(
            self.current_camera
        )

    # =====================================
    # OPEN CAMERA SOURCE
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

            # Release previous capture
            if self.cap:

                self.cap.release()

            # ==========================
            # VIDEO FILE
            # ==========================

            if source_type == "video":

                self.cap = cv2.VideoCapture(
                    source_path
                )

            # ==========================
            # WEBCAM
            # ==========================

            elif source_type == "webcam":

                self.cap = cv2.VideoCapture(
                    int(source_path)
                )

            # ==========================
            # RTSP
            # ==========================

            elif source_type == "rtsp":

                if not source_path:

                    print(
                        "[ERROR] RTSP URL empty"
                    )

                    return False

                self.cap = cv2.VideoCapture(
                    source_path
                )

            else:

                print(
                    f"[ERROR] Unsupported source type: {source_type}"
                )

                return False

            # ==========================
            # VALIDATION
            # ==========================

            if not self.cap.isOpened():

                print(
                    f"[ERROR] Cannot open source: {source_path}"
                )

                return False

            print(
                f"[INFO] Opened source: {source_id}"
            )

            return True

        except Exception as e:

            print(
                f"[ERROR] Failed opening source: {e}"
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

        # =====================================
        # LOOP VIDEO FILES
        # =====================================

        if not ret:

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

            print(
                f"[ERROR] Unknown camera: {camera_id}"
            )

            return False

        old_camera = self.current_camera

        success = self.open_source(
            camera_id
        )

        if success:

            self.current_camera = camera_id

            print(
                f"[INFO] Switched to camera: {camera_id}" )


        else:
            self.current_camera = old_camera

            print(
                f"[INFO] Failed to switch to camera: {camera_id}"
            )

        return success

    # =====================================
    # RTSP URL UPDATE
    # =====================================

    def set_rtsp_url(
        self,
        rtsp_url
    ):

        self.sources["rtsp"][
            "path"
        ] = rtsp_url

    # =====================================
    # PAUSE
    # =====================================

    def pause(self):

        self.paused = True

        print(
            "[INFO] Stream Paused"
        )

    # =====================================
    # PLAY
    # =====================================

    def play(self):

        self.paused = False

        print(
            "[INFO] Stream Playing"
        )

    # =====================================
    # RESTART
    # =====================================

    def restart_camera(self):

        print(
            "[INFO] Restarting Camera"
        )

        return self.open_source(
            self.current_camera
        )

    # =====================================
    # RELEASE
    # =====================================

    def release(self):

        if self.cap:

            self.cap.release()

            self.cap = None


# =====================================
# GLOBAL CAMERA MANAGER
# =====================================

camera_manager = CameraManager()