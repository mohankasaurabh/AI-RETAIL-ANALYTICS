import cv2
import numpy as np


class TemporalHeatmap:

    def __init__(self, width=1280, height=720):

        self.width = width

        self.height = height

    def generate(
        self,
        background_frame,
        movement_logs
    ):

        heatmap = np.zeros(
            (self.height, self.width),
            dtype=np.float32
        )

        # Add trajectory heat
        for log in movement_logs:

            x = log["x"]

            y = log["y"]

            cv2.circle(
                heatmap,
                (x, y),
                20,
                1,
                -1
            )

        # Smooth heatmap
        heatmap = cv2.GaussianBlur(
            heatmap,
            (41, 41),
            0
        )

        # Normalize
        normalized = cv2.normalize(
            heatmap,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

        normalized = normalized.astype(np.uint8)

        # Color map
        colored = cv2.applyColorMap(
            normalized,
            cv2.COLORMAP_JET
        )

        # Overlay
        overlay = cv2.addWeighted(
            background_frame,
            0.7,
            colored,
            0.6,
            0
        )

        return overlay