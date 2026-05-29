import cv2

from ai_engine.utils.line_drawer import LineDrawer


drawer = LineDrawer()

cap = cv2.VideoCapture("data/videos/mall.mp4")

ret, frame = cap.read()

frame = cv2.resize(frame, (1280, 720))

cv2.namedWindow("Draw Counting Line")

cv2.setMouseCallback(
    "Draw Counting Line",
    drawer.mouse_callback
)

while True:

    display_frame = frame.copy()

    drawer.draw(display_frame)

    cv2.imshow("Draw Counting Line", display_frame)

    key = cv2.waitKey(1)

    # Press S to save
    if key == ord("s"):

        drawer.save_config()

        break

    # Press Q to quit
    if key == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()