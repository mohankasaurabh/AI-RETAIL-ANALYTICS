import time


class IdentityMemory:

    def __init__(self, max_inactive_time=30):

        self.active_identities = {}

        self.max_inactive_time = max_inactive_time

    def update_identity(self, identity_id):

        self.active_identities[identity_id] = time.time()

    def cleanup(self):

        current_time = time.time()

        expired = []

        for identity_id, last_seen in self.active_identities.items():

            if current_time - last_seen > self.max_inactive_time:

                expired.append(identity_id)

        for identity_id in expired:

            del self.active_identities[identity_id]

        return expired

    def is_active(self, identity_id):

        return identity_id in self.active_identities