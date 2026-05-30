import cv2
import numpy as np

from ai_engine.reid.osnet import (
    OSNetFeatureExtractor
)


class FeatureExtractor:

    def __init__(self):

        self.osnet = (
            OSNetFeatureExtractor()
        )

    # =====================================
    # EXTRACT PERSON FEATURES
    # =====================================

    def extract(
        self,
        frame,
        bbox
    ):

        try:

            x1, y1, x2, y2 = bbox

            h, w = frame.shape[:2]

            # =====================================
            # SAFE BOUNDS
            # =====================================

            x1 = max(0, x1)
            y1 = max(0, y1)

            x2 = min(w, x2)
            y2 = min(h, y2)

            if x2 <= x1:

                return None

            if y2 <= y1:

                return None

            # =====================================
            # PERSON CROP
            # =====================================

            crop = frame[
                y1:y2,
                x1:x2
            ]

            if crop.size == 0:

                return None

            # =====================================
            # RESIZE
            # =====================================

            crop = cv2.resize(
                crop,
                (128, 256)
            )

            # =====================================
            # OSNET EMBEDDING
            # =====================================

            features = (
                self.osnet.extract(
                    crop
                )
            )

            if features is None:

                return None

            # =====================================
            # NORMALIZE VECTOR
            # =====================================

            norm = np.linalg.norm(
                features
            )

            if norm == 0:

                return None

            features = (
                features / norm
            )

            return features

        except Exception as e:

            print(
                f"[REID ERROR] "
                f"{e}"
            )

            return None