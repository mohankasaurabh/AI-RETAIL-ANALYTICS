import yaml


class FootfallCounter:

    def __init__(self):

        with open("configs/line_config.yaml", "r") as file:

            config = yaml.safe_load(file)

        self.line_start = tuple(config["line_start"])

        self.line_end = tuple(config["line_end"])

        self.entry_count = 0

        self.exit_count = 0

        self.current_occupancy = 0

        self.track_positions = {}

    def update(self, track_id, centroid):

        center_x, center_y = centroid

        line_y = self.line_start[1]

        if track_id not in self.track_positions:

            self.track_positions[track_id] = center_y

            return

        previous_y = self.track_positions[track_id]

        # ENTRY
        if previous_y < line_y and center_y >= line_y:

            self.entry_count += 1

            self.current_occupancy += 1

        # EXIT
        elif previous_y > line_y and center_y <= line_y:

            self.exit_count += 1

            self.current_occupancy = max(
                0,
                self.current_occupancy - 1
            )

        self.track_positions[track_id] = center_y

    def get_counts(self):

        return {
            "entries": self.entry_count,
            "exits": self.exit_count,
            "occupancy": self.current_occupancy
        }