from ai_engine.association.customer_profile import CustomerProfile


class IdentityManager:

    def __init__(self):

        self.customers = {}

    def update_customer(self, track_id, centroid):

        if track_id not in self.customers:

            self.customers[track_id] = CustomerProfile(track_id)

        self.customers[track_id].update(centroid)

    def get_customer(self, track_id):

        if track_id in self.customers:

            return self.customers[track_id].get_profile()

        return None

    def get_all_customers(self):

        profiles = []

        for customer in self.customers.values():

            profiles.append(customer.get_profile())

        return profiles