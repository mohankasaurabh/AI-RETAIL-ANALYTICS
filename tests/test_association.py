import cv2

from ai_engine.tracking.tracker import CustomerTracker

from ai_engine.tracking.tracking_utils import (
    draw_tracking_box,
    get_centroid,
    update_trajectory,
    draw_centroid,
    draw_trajectory
)

from ai_engine.association.identity_manager import IdentityManager

from ai_engine.association.session_manager import SessionManager


tracker = CustomerTracker()

identity_manager = IdentityManager()

session_manager = SessionManager(timeout=5)

cap = cv2.VideoCapture("data/videos/mall.mp4")


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))

    tracked_objects = tracker.track(frame)

    for obj in tracked_objects:

        track_id = obj["track_id"]

        bbox = obj["bbox"]

        centroid = get_centroid(bbox)

        update_trajectory(track_id, centroid)

        identity_manager.update_customer(
            track_id,
            centroid
        )

        draw_tracking_box(frame, track_id, bbox)

        draw_centroid(frame, centroid)

        draw_trajectory(frame, track_id)

        customer = identity_manager.get_customer(track_id)

        if customer:

            cv2.putText(
                frame,
                f"Dwell: {customer['dwell_time']}s",
                (bbox[0], bbox[1] - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )

    removed = session_manager.remove_inactive_customers(
        identity_manager.customers
    )

    cv2.putText(
        frame,
        f"Active Customers: {len(identity_manager.customers)}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.imshow("Retail Association Engine", frame)

    if cv2.waitKey(1) == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()