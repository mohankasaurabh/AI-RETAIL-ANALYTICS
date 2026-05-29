import cv2

from ai_engine.tracking.tracker import CustomerTracker

from ai_engine.tracking.tracking_utils import (
    draw_tracking_box,
    get_centroid,
    draw_centroid
)

from ai_engine.reid.reid_model import ReIDManager


# Initialize tracker
tracker = CustomerTracker()

# Initialize ReID manager
reid = ReIDManager()

# Load retail video
cap = cv2.VideoCapture("data/videos/mall.mp4")


while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Resize frame
    frame = cv2.resize(frame, (1280, 720))

    # Run tracking
    tracked_objects = tracker.track(frame)

    for obj in tracked_objects:

        bbox = obj["bbox"]

        track_id = obj["track_id"]

        # Match ReID identity
        reid_id = reid.match_identity(
            frame,
            track_id,
            bbox
        )

        # Skip invalid identities
        if reid_id is None:
            continue

        # Get centroid
        centroid = get_centroid(bbox)

        # Draw tracking info
        draw_tracking_box(
            frame,
            f"T{track_id} | R{reid_id}",
            bbox
        )

        # Draw centroid
        draw_centroid(frame, centroid)

    # Cleanup inactive identities
    expired = reid.cleanup_inactive_identities()

    # Display active identity count
    cv2.putText(
        frame,
        f"Active ReID Identities: {len(reid.feature_bank.bank)}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        3
    )

    # Display output
    cv2.imshow("Retail ReID System", frame)

    # Quit
    if cv2.waitKey(1) == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()