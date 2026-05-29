import cv2
import yaml


class ZoneDrawer:

    def __init__(self):

        self.points = []

    def mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:

            self.points.append((x, y))

            print(f"[INFO] Point Added: {(x, y)}")

    def draw(self, frame):

        # Draw points
        for point in self.points:

            cv2.circle(
                frame,
                point,
                5,
                (0, 0, 255),
                -1
            )

        # Draw polygon lines
        if len(self.points) > 1:

            for i in range(len(self.points) - 1):

                cv2.line(
                    frame,
                    self.points[i],
                    self.points[i + 1],
                    (0, 255, 0),
                    2
                )

        # Close polygon
        if len(self.points) > 2:

            cv2.line(
                frame,
                self.points[-1],
                self.points[0],
                (0, 255, 0),
                2
            )

    def save_config(self, path="configs/zone_config.yaml"):

        config = {
            "zone_points": [
                list(point)
                for point in self.points
            ]
        }

        with open(path, "w") as file:

            yaml.dump(config, file)

        print(f"[INFO] Zone Saved -> {path}")