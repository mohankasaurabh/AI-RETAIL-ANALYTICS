import numpy as np


class FeatureBank:

    def __init__(self, max_features=20):

        self.bank = {}

        self.max_features = max_features

    def add_feature(self, identity_id, feature):

        if identity_id not in self.bank:

            self.bank[identity_id] = []

        self.bank[identity_id].append(feature)

        # Keep latest embeddings only
        if len(self.bank[identity_id]) > self.max_features:

            self.bank[identity_id].pop(0)

    def get_average_feature(self, identity_id):

        if identity_id not in self.bank:
            return None

        features = self.bank[identity_id]

        return np.mean(features, axis=0)

    def get_all_identities(self):

        return self.bank.keys()