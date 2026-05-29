import cv2
import numpy as np


class HeatmapGenerator:

    def __init__(self):

        self.heatmap = None

    # =====================================
    # INITIALIZE HEATMAP
    # =====================================

    def initialize_heatmap(
        self,
        frame_shape
    ):

        height, width = frame_shape[:2]

        self.heatmap = np.zeros(

            (height, width),

            dtype=np.float32
        )

    # =====================================
    # UPDATE HEATMAP
    # =====================================

    def update(
        self,
        centroid
    ):

        x, y = centroid

        if self.heatmap is None:

            return

        cv2.circle(

            self.heatmap,

            (x, y),

            35,

            1,

            -1
        )

    # =====================================
    # APPLY DECAY
    # =====================================

    def apply_decay(self):

        self.heatmap *= 0.995

    # =====================================
    # GENERATE OVERLAY
    # =====================================

    def overlay_heatmap(
        self,
        frame
    ):

        if self.heatmap is None:

            self.initialize_heatmap(
                frame.shape
            )

        self.apply_decay()

        normalized = cv2.normalize(

            self.heatmap,

            None,

            0,

            255,

            cv2.NORM_MINMAX
        )

        heatmap_uint8 = np.uint8(
            normalized
        )

        colored_heatmap = cv2.applyColorMap(

            heatmap_uint8,

            cv2.COLORMAP_JET
        )

        overlay = cv2.addWeighted(

            frame,

            0.7,

            colored_heatmap,

            0.3,

            0
        )

        return overlay