import time


class QueueAnalytics:

    def __init__(self):

        # Queue area
        self.queue_zone = (

            (950, 250),

            (1280, 720)
        )

        self.waiting_customers = {}

        self.queue_length = 0

        self.average_wait = 0

    # =====================================
    # CHECK INSIDE QUEUE
    # =====================================

    def inside_queue_zone(
        self,
        centroid
    ):

        x, y = centroid

        (x1, y1), (x2, y2) = (
            self.queue_zone
        )

        return (

            x1 <= x <= x2

            and

            y1 <= y <= y2
        )

    # =====================================
    # UPDATE
    # =====================================

    def update(
        self,
        reid_id,
        centroid
    ):

        current_time = time.time()

        inside = self.inside_queue_zone(
            centroid
        )

        if inside:

            if reid_id not in self.waiting_customers:

                self.waiting_customers[
                    reid_id
                ] = current_time

        else:

            if reid_id in self.waiting_customers:

                del self.waiting_customers[
                    reid_id
                ]

        self.queue_length = len(
            self.waiting_customers
        )

        waits = []

        for start_time in (
            self.waiting_customers.values()
        ):

            waits.append(

                current_time -
                start_time
            )

        if waits:

            self.average_wait = (
                sum(waits) /
                len(waits)
            )

        else:

            self.average_wait = 0

    # =====================================
    # STATUS
    # =====================================

    def get_status(self):

        if self.queue_length >= 10:

            return "HIGH"

        elif self.queue_length >= 5:

            return "MEDIUM"

        return "LOW"

    # =====================================
    # DRAW
    # =====================================

    def draw_queue_zone(
        self,
        frame
    ):

        (x1, y1), (x2, y2) = (
            self.queue_zone
        )

        import cv2

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            (0, 0, 255),

            3
        )

        cv2.putText(

            frame,

            "QUEUE AREA",

            (x1 + 10, y1 + 30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 0, 255),

            2
        )

        return frame