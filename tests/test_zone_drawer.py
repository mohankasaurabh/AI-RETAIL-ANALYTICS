import cv2

from ai_engine.utils.zone_drawer import ZoneDrawer


drawer = ZoneDrawer()

cap = cv2.VideoCapture("data/videos/mall.mp4")

ret, frame = cap.read()

frame = cv2.resize(frame, (1280, 720))

cv2.namedWindow("Draw Retail Zone")

cv2.setMouseCallback(
    "Draw Retail Zone",
    drawer.mouse_callback
)

while True:

    display_frame = frame.copy()

    drawer.draw(display_frame)

    cv2.imshow(
        "Draw Retail Zone",
        display_frame
    )

    key = cv2.waitKey(1)

    # Save zone
    if key == ord("s"):

        drawer.save_config()

        break

    # Quit
    if key == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()