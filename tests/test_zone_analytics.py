import cv2
import numpy as np

from ai_engine.tracking.tracker import CustomerTracker

from ai_engine.tracking.tracking_utils import (
    draw_tracking_box,
    get_centroid,
    draw_centroid,
    draw_trajectory,
    update_trajectory
)

from ai_engine.analytics.zone_analytics import ZoneAnalytics


tracker = CustomerTracker()

zone = ZoneAnalytics()

cap = cv2.VideoCapture("data/videos/mall.mp4")


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))

    tracked_objects = tracker.track(frame)

    # Draw zone polygon
    zone_points = np.array(
        zone.zone_points,
        np.int32
    )

    cv2.polylines(
        frame,
        [zone_points],
        isClosed=True,
        color=(0, 255, 255),
        thickness=3
    )

    for obj in tracked_objects:

        track_id = obj["track_id"]

        bbox = obj["bbox"]

        centroid = get_centroid(bbox)

        update_trajectory(track_id, centroid)

        zone.update(track_id, centroid)

        draw_tracking_box(
            frame,
            track_id,
            bbox
        )

        draw_centroid(frame, centroid)

        draw_trajectory(frame, track_id)

    stats = zone.get_zone_statistics()

    # Analytics display
    cv2.putText(
        frame,
        f"Zone Occupancy: {stats['active_customers']}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.putText(
        frame,
        f"Zone Visits: {stats['total_visits']}",
        (30, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        3
    )

    cv2.putText(
        frame,
        f"Avg Dwell: {stats['average_dwell']}s",
        (30, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )

    cv2.imshow(
        "Retail Zone Analytics",
        frame
    )

    if cv2.waitKey(1) == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()