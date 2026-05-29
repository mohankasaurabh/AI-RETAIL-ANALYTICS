import cv2

from ai_engine.tracking.tracker import CustomerTracker

from ai_engine.tracking.tracking_utils import (
    get_centroid
)

from ai_engine.analytics.heatmap_generator import (
    HeatmapGenerator
)


# Initialize tracker
tracker = CustomerTracker()

# Initialize heatmap engine
heatmap = HeatmapGenerator()


# Load mall video
cap = cv2.VideoCapture("data/videos/mall.mp4")


# Read first frame for persistent background
ret, first_frame = cap.read()

if not ret:

    print("[ERROR] Unable to read video.")

    exit()

# Resize background frame
first_frame = cv2.resize(
    first_frame,
    (1280, 720)
)

# Store clean background
background_frame = first_frame.copy()

# Reset video back to beginning
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Resize frame
    frame = cv2.resize(
        frame,
        (1280, 720)
    )

    # Run tracking
    tracked_objects = tracker.track(frame)

    for obj in tracked_objects:

        bbox = obj["bbox"]

        centroid = get_centroid(bbox)

        # Update heatmaps
        track_id = obj["track_id"]
        heatmap.update(
            track_id,
            centroid
        )

    # =========================
    # LIVE HEATMAP
    # =========================

    live_output = heatmap.generate_live_overlay(
        frame
    )

    cv2.imshow(
        "Live Retail Heatmap",
        live_output
    )

    # =========================
    # PERSISTENT HEATMAP
    # =========================

    persistent_output = (
        heatmap.generate_persistent_overlay(
            background_frame
        )
    )

    cv2.imshow(
        "Persistent Retail Heatmap",
        persistent_output
    )

    # Keyboard controls
    key = cv2.waitKey(1)

    # Save persistent heatmap
    if key == ord("s"):

        heatmap.save_persistent_heatmap(
            background_frame
        )

    # Quit
    if key == ord("q"):
        break

cap.release()

cv2.destroyAllWindows()