import cv2


class ZoneAnalytics:

    def __init__(self):

        # =====================================
        # DEFINE ZONES
        # =====================================

        self.zones = {

            "Zone A": (

                (0, 0),

                (400, 350)
            ),

            "Zone B": (

                (400, 0),

                (800, 350)
            ),

            "Zone C": (

                (800, 0),

                (1280, 350)
            ),

            "Zone D": (

                (0, 350),

                (1280, 720)
            )
        }

        self.zone_counts = {

            zone: 0

            for zone in self.zones
        }

    # =====================================
    # RESET COUNTS
    # =====================================

    def reset_counts(self):

        for zone in self.zone_counts:

            self.zone_counts[zone] = 0

    # =====================================
    # UPDATE ZONES
    # =====================================

    def update(self, centroid):

        x, y = centroid

        for zone_name, coords in (
            self.zones.items()
        ):

            (x1, y1), (x2, y2) = coords

            if (

                x1 <= x <= x2

                and

                y1 <= y <= y2
            ):

                self.zone_counts[
                    zone_name
                ] += 1

                break

    # =====================================
    # DRAW ZONES
    # =====================================

    def draw_zones(self, frame):

        for zone_name, coords in (
            self.zones.items()
        ):

            (x1, y1), (x2, y2) = coords

            count = self.zone_counts[
                zone_name
            ]

            # Draw rectangle
            cv2.rectangle(

                frame,

                (x1, y1),

                (x2, y2),

                (0, 255, 255),

                2
            )

            # Draw zone label
            cv2.putText(

                frame,

                f"{zone_name}: {count}",

                (x1 + 10, y1 + 30),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.8,

                (0, 255, 255),

                2
            )

        return frame

    # =====================================
    # GET TOTAL OCCUPANCY
    # =====================================

    def get_total_occupancy(self):

        return sum(
            self.zone_counts.values()
        )
    

    # =====================================
    # GET ZONE FROM CENTROID
    # =====================================

    def get_zone(
        self,
        centroid
    ):

        x, y = centroid

        for zone_name, coords in (
            self.zones.items()
        ):

            (x1, y1), (x2, y2) = coords

            if (

                x1 <= x <= x2

                and

                y1 <= y <= y2
            ):

                return zone_name

        return "Unknown"