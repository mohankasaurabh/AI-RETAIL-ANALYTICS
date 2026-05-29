import numpy as np


class SimilarityMatcher:

    @staticmethod
    def cosine_similarity(a, b):

        return np.dot(a, b.T) / (
            np.linalg.norm(a) * np.linalg.norm(b)
        )

    def find_best_match(
        self,
        query_feature,
        feature_bank,
        threshold=0.85
    ):

        best_match = None

        best_score = 0

        for identity_id in feature_bank.get_all_identities():

            stored_feature = feature_bank.get_average_feature(
                identity_id
            )

            score = self.cosine_similarity(
                query_feature.flatten(),
                stored_feature.flatten()
            )

            if score > best_score:

                best_score = score

                best_match = identity_id

        if best_score >= threshold:

            return best_match, best_score

        return None, best_score