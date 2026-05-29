import time


class CustomerProfile:

    def __init__(self, track_id):

        self.track_id = track_id

        self.entry_time = time.time()

        self.last_seen = time.time()

        self.dwell_time = 0

        self.trajectory = []

        self.zones_visited = []

    def update(self, centroid):

        self.last_seen = time.time()

        self.dwell_time = int(
            self.last_seen - self.entry_time
        )

        self.trajectory.append(centroid)

    def get_profile(self):

        return {
            "track_id": self.track_id,
            "dwell_time": self.dwell_time,
            "trajectory_length": len(self.trajectory),
            "zones_visited": self.zones_visited
        }