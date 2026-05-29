import cv2
import time

from ai_engine.tracking.tracker import CustomerTracker

from ai_engine.tracking.tracking_utils import (
    get_centroid
)

from ai_engine.analytics.movement_logger import (
    MovementLogger
)

from ai_engine.analytics.temporal_heatmap import (
    TemporalHeatmap
)


tracker = CustomerTracker()

logger = MovementLogger()

temporal_heatmap = TemporalHeatmap()


cap = cv2.VideoCapture("data/videos/mall.mp4")


# Background frame
ret, first_frame = cap.read()

first_frame = cv2.resize(
    first_frame,
    (1280, 720)
)

background_frame = first_frame.copy()

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


start_time = time.time()


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(
        frame,
        (1280, 720)
    )

    tracked_objects = tracker.track(frame)

    for obj in tracked_objects:

        track_id = obj["track_id"]

        bbox = obj["bbox"]

        centroid = get_centroid(bbox)

        # Log movement
        logger.log(
            track_id,
            centroid
        )

    # Last 20 seconds analytics
    current_time = time.time()

    recent_logs = logger.get_logs_between(
        current_time - 20,
        current_time
    )

    # Generate temporal heatmap
    temporal_output = temporal_heatmap.generate(
        background_frame,
        recent_logs
    )

    cv2.putText(
        temporal_output,
        "Temporal Heatmap (Last 20s)",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        3
    )

    cv2.imshow(
        "Temporal Retail Heatmap",
        temporal_output
    )

    key = cv2.waitKey(1)

    if key == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()