import cv2
import yaml


class LineDrawer:

    def __init__(self):

        self.points = []

    def mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:

            if len(self.points) < 2:

                self.points.append((x, y))

                print(f"[INFO] Point Added: {(x, y)}")

    def draw(self, frame):

        # Draw selected points
        for point in self.points:

            cv2.circle(
                frame,
                point,
                6,
                (0, 0, 255),
                -1
            )

        # Draw line if 2 points selected
        if len(self.points) == 2:

            cv2.line(
                frame,
                self.points[0],
                self.points[1],
                (0, 255, 0),
                3
            )

    def save_config(self, path="configs/line_config.yaml"):

        if len(self.points) != 2:

            print("[ERROR] Select exactly 2 points.")

            return

        config = {
            "line_start": list(self.points[0]),
            "line_end": list(self.points[1])
        }

        with open(path, "w") as file:

            yaml.dump(config, file)

        print(f"[INFO] Line Config Saved -> {path}")