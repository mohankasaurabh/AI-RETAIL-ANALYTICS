from ai_engine.reid.feature_extractor import (
    FeatureExtractor
)

from ai_engine.reid.global_identity import (
    global_registry
)


class ReIDManager:

    def __init__(self):

        self.extractor = (
            FeatureExtractor()
        )

        # Shared Global Registry
        self.global_registry = (
            global_registry
        )

    # =====================================
    # MATCH IDENTITY
    # =====================================

    def match_identity(
        self,
        frame,
        bbox,
        camera_id
    ):

        x1, y1, x2, y2 = bbox

        # Safety clamp
        h, w = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(w, x2)
        y2 = min(h, y2)

        crop = frame[
            y1:y2,
            x1:x2
        ]

        if crop.size == 0:

            return None

        # =====================================
        # FEATURE EXTRACTION
        # =====================================

        features = (
            self.extractor.extract(
                crop
            )
        )

        if features is None:

            return None

        # =====================================
        # GLOBAL MATCH
        # =====================================

        global_id = (
            self.global_registry.match(

                features,

                camera_id
            )
        )

        return global_id

    # =====================================
    # TOTAL IDENTITIES
    # =====================================

    def total_identities(
        self
    ):

        return (
            self.global_registry
            .total_identities()
        )

    # =====================================
    # MULTI CAMERA CUSTOMERS
    # =====================================

    def total_multi_camera_customers(
        self
    ):

        return (
            self.global_registry
            .total_multi_camera_customers()
        )

    # =====================================
    # CLEANUP
    # =====================================

    def cleanup(
        self
    ):

        self.global_registry.cleanup()

    # =====================================
    # STATS
    # =====================================

    def get_statistics(
        self
    ):

        return (
            self.global_registry
            .get_statistics()
        )