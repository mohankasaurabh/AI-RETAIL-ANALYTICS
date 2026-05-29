import cv2


class RTSPStream:

    def __init__(
        self,
        rtsp_url
    ):

        self.rtsp_url = rtsp_url

        self.cap = cv2.VideoCapture(
            rtsp_url
        )

    def read(self):

        ret, frame = self.cap.read()

        if not ret:

            return None

        return frame

    def release(self):

        self.cap.release()