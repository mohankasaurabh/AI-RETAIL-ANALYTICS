import time


class MovementLogger:

    def __init__(self):

        self.logs = []

    def log(self, track_id, centroid):

        x, y = centroid

        entry = {
            "timestamp": time.time(),
            "track_id": track_id,
            "x": x,
            "y": y
        }

        self.logs.append(entry)

    def get_logs_between(
        self,
        start_time,
        end_time
    ):

        filtered = []

        for log in self.logs:

            if start_time <= log["timestamp"] <= end_time:

                filtered.append(log)

        return filtered

    def get_all_logs(self):

        return self.logs