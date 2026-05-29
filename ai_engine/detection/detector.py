from ai_engine.detection.yolo_loader import YOLOLoader
from ai_engine.detection.classes import PERSON_CLASS_ID


class PersonDetector:

    def __init__(self):

        self.model = YOLOLoader().get_model()

    def detect(self, frame):

        results = self.model(
        frame,
        imgsz=1280,
        conf=0.4
    )

        detections = []

        for result in results:

            boxes = result.boxes

            for box in boxes:

                class_id = int(box.cls[0])

                if class_id != PERSON_CLASS_ID:
                    continue

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append({
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

        return detections