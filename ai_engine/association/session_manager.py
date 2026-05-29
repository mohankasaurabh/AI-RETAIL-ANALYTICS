import time


class SessionManager:

    def __init__(self, timeout=10):

        self.timeout = timeout

    def remove_inactive_customers(self, customers):

        current_time = time.time()

        inactive_ids = []

        for track_id, customer in customers.items():

            if current_time - customer.last_seen > self.timeout:

                inactive_ids.append(track_id)

        for track_id in inactive_ids:

            del customers[track_id]

        return inactive_ids