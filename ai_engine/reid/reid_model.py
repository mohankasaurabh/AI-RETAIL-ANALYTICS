from ai_engine.reid.feature_extractor import (
    FeatureExtractor
)

from ai_engine.reid.global_identity import (
    global_registry
)


class ReIDManager:

    def __init__(self):

        # =====================================
        # FEATURE EXTRACTOR
        # =====================================

        self.extractor = (
            FeatureExtractor()
        )

        # =====================================
        # GLOBAL IDENTITY REGISTRY
        # =====================================

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

        try:

            # =====================================
            # FEATURE EXTRACTION
            # =====================================

            features = (
                self.extractor.extract(

                    frame,

                    bbox
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

        except Exception as e:

            print(
                f"[REID ERROR] {e}"
            )

            return None

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
    # STATISTICS
    # =====================================

    def get_statistics(
        self
    ):

        return (
            self.global_registry
            .get_statistics()
        )