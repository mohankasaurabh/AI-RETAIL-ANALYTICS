import cv2

from ai_engine.detection.detector import PersonDetector


detector = PersonDetector()

cap = cv2.VideoCapture("data/videos/mall.mp4")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (1280, 720))
    detections = detector.detect(frame)

    for det in detections:

        x1, y1, x2, y2 = det["bbox"]

        confidence = det["confidence"]

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Person {confidence:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    cv2.imshow("Retail Detection Engine", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()