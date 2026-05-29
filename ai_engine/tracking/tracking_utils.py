import cv2


# Store trajectory history
track_history = {}


def get_centroid(bbox):

    x1, y1, x2, y2 = bbox

    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    return (center_x, center_y)


def update_trajectory(track_id, centroid):

    if track_id not in track_history:
        track_history[track_id] = []

    track_history[track_id].append(centroid)

    # Keep only latest 30 points
    if len(track_history[track_id]) > 30:
        track_history[track_id].pop(0)


def draw_tracking_box(frame, track_id, bbox):

    x1, y1, x2, y2 = bbox

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"ID {track_id}",
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


def draw_centroid(frame, centroid):

    cv2.circle(
        frame,
        centroid,
        5,
        (0, 0, 255),
        -1
    )


def draw_trajectory(frame, track_id):

    if track_id not in track_history:
        return

    points = track_history[track_id]

    for i in range(1, len(points)):

        cv2.line(
            frame,
            points[i - 1],
            points[i],
            (255, 0, 0),
            2
        )