import cv2

from ai_engine.tracking.tracker import CustomerTracker

from ai_engine.tracking.tracking_utils import (
    draw_tracking_box,
    get_centroid,
    update_trajectory,
    draw_centroid,
    draw_trajectory
)

from ai_engine.analytics.footfall_counter import FootfallCounter


tracker = CustomerTracker()

counter = FootfallCounter()

cap = cv2.VideoCapture("data/videos/mall.mp4")


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))

    tracked_objects = tracker.track(frame)

    # Draw configured counting line
    cv2.line(
        frame,
        counter.line_start,
        counter.line_end,
        (0, 0, 255),
        3
    )

    for obj in tracked_objects:

        track_id = obj["track_id"]

        bbox = obj["bbox"]

        centroid = get_centroid(bbox)

        update_trajectory(track_id, centroid)

        counter.update(track_id, centroid)

        draw_tracking_box(frame, track_id, bbox)

        draw_centroid(frame, centroid)

        draw_trajectory(frame, track_id)

    counts = counter.get_counts()

    # Display analytics
    cv2.putText(
        frame,
        f"Entries: {counts['entries']}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.putText(
        frame,
        f"Exits: {counts['exits']}",
        (30, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )

    cv2.putText(
        frame,
        f"Occupancy: {counts['occupancy']}",
        (30, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        3
    )

    cv2.imshow("Retail Footfall Analytics", frame)

    if cv2.waitKey(1) == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()