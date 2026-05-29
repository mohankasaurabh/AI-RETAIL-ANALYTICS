import time


class CustomerJourney:

    def __init__(self):

        # =====================================
        # CUSTOMER JOURNEYS
        # =====================================

        self.customers = {}

    # =====================================
    # UPDATE JOURNEY
    # =====================================

    def update(
        self,
        customer_id,
        current_zone
    ):

        current_time = time.time()

        # =====================================
        # NEW CUSTOMER
        # =====================================

        if customer_id not in self.customers:

            self.customers[customer_id] = {

                "entry_time":
                    current_time,

                "current_zone":
                    current_zone,

                "visited_zones":
                    [current_zone],

                "zone_times":
                    {
                        current_zone:
                            current_time
                    }
            }

            return

        customer = self.customers[
            customer_id
        ]

        previous_zone = customer[
            "current_zone"
        ]

        # =====================================
        # ZONE CHANGED
        # =====================================

        if current_zone != previous_zone:

            customer[
                "current_zone"
            ] = current_zone

            customer[
                "visited_zones"
            ].append(current_zone)

            customer[
                "zone_times"
            ][current_zone] = current_time

    # =====================================
    # GET CUSTOMER JOURNEY
    # =====================================

    def get_journey(
        self,
        customer_id
    ):

        return self.customers.get(
            customer_id,
            None
        )

    # =====================================
    # GET TOTAL CUSTOMERS
    # =====================================

    def total_customers(self):

        return len(self.customers)