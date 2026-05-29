import cv2

from ai_engine.tracking.tracker import CustomerTracker
from ai_engine.tracking.tracking_utils import draw_tracking_box


tracker = CustomerTracker()

cap = cv2.VideoCapture("data/videos/mall.mp4")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))

    tracked_objects = tracker.track(frame)

    for obj in tracked_objects:

        draw_tracking_box(
            frame,
            obj["track_id"],
            obj["bbox"]
        )

    cv2.imshow("Retail Tracking Engine", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()