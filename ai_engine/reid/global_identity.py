import time
import numpy as np


class GlobalIdentityRegistry:

    def __init__(self):

        # =====================================
        # GLOBAL IDENTITIES
        # =====================================

        self.identities = {}

        self.next_id = 1

        self.threshold = 0.65

        self.timeout = 300

    # =====================================
    # COSINE SIMILARITY
    # =====================================

    def cosine_similarity(
        self,
        vec1,
        vec2
    ):

        dot = np.dot(
            vec1,
            vec2
        )

        norm1 = np.linalg.norm(
            vec1
        )

        norm2 = np.linalg.norm(
            vec2
        )

        return dot / (
            norm1 * norm2 + 1e-6
        )

    # =====================================
    # UPDATE FEATURE BANK
    # =====================================

    def update_identity(
        self,
        identity_id,
        feature
    ):

        identity = self.identities[
            identity_id
        ]

        bank = identity[
            "feature_bank"
        ]

        bank.append(
            feature
        )

        # Keep latest observations
        if len(bank) > 30:

            bank.pop(0)

        avg_feature = np.mean(

            np.array(bank),

            axis=0
        )

        identity[
            "avg_feature"
        ] = avg_feature

        identity[
            "last_seen"
        ] = time.time()

    # =====================================
    # CREATE NEW IDENTITY
    # =====================================

    def create_identity(
        self,
        feature,
        camera_id
    ):

        identity_id = self.next_id

        self.identities[
            identity_id
        ] = {

            "feature_bank": [

                feature
            ],

            "avg_feature":

                feature,

            "last_seen":

                time.time(),

            "camera_history":

                {camera_id}
        }

        self.next_id += 1

        return identity_id

    # =====================================
    # MATCH GLOBAL IDENTITY
    # =====================================

    def match(
        self,
        feature,
        camera_id
    ):

        best_score = 0

        best_identity = None

        # =====================================
        # SEARCH EXISTING IDS
        # =====================================

        for identity_id, data in (

            self.identities.items()
        ):

            score = self.cosine_similarity(

                feature,

                data["avg_feature"]
            )

            if score > best_score:

                best_score = score

                best_identity = identity_id

        # =====================================
        # MATCH FOUND
        # =====================================

        if (

            best_identity is not None

            and

            best_score >= self.threshold
        ):

            self.update_identity(

                best_identity,

                feature
            )

            self.identities[
                best_identity
            ][
                "camera_history"
            ].add(
                camera_id
            )

            return best_identity

        # =====================================
        # NEW IDENTITY
        # =====================================

        return self.create_identity(

            feature,

            camera_id
        )

    # =====================================
    # GET IDENTITY
    # =====================================

    def get_identity(
        self,
        identity_id
    ):

        return self.identities.get(
            identity_id
        )

    # =====================================
    # TOTAL IDENTITIES
    # =====================================

    def total_identities(
        self
    ):

        return len(
            self.identities
        )

    # =====================================
    # MULTI CAMERA CUSTOMERS
    # =====================================

    def total_multi_camera_customers(
        self
    ):

        count = 0

        for identity in (

            self.identities.values()
        ):

            if len(

                identity[
                    "camera_history"
                ]

            ) > 1:

                count += 1

        return count

    # =====================================
    # CLEANUP OLD IDENTITIES
    # =====================================

    def cleanup(
        self
    ):

        current_time = time.time()

        remove_ids = []

        for identity_id, data in (

            self.identities.items()
        ):

            if (

                current_time

                -

                data["last_seen"]

                >

                self.timeout
            ):

                remove_ids.append(
                    identity_id
                )

        for identity_id in remove_ids:

            del self.identities[
                identity_id
            ]

    # =====================================
    # DEBUG INFO
    # =====================================

    def get_statistics(
        self
    ):

        return {

            "total_identities":

                self.total_identities(),

            "multi_camera_customers":

                self.total_multi_camera_customers()
        }


# =====================================
# SINGLE GLOBAL REGISTRY
# SHARED BY ALL CAMERAS
# =====================================

global_registry = (
    GlobalIdentityRegistry()
)