from ai_engine.demographics.face_detector import (
    FaceDetector
)

from ai_engine.demographics.deepface_engine import (
    DeepFaceEngine
)


class DemographicsAnalyzer:

    def __init__(self):

        self.face_detector = FaceDetector()

        self.deepface = DeepFaceEngine()

    # =====================================
    # ANALYZE PERSON ROI
    # =====================================

    def analyze_person(
        self,
        frame,
        bbox,
        track_id
    ):

        x1, y1, x2, y2 = bbox

        # Crop person ROI
        person_crop = frame[
            y1:y2,
            x1:x2
        ]

        if person_crop.size == 0:

            return None

        # Detect faces INSIDE person ROI
        faces = self.face_detector.detect_faces(
            person_crop
        )

        if len(faces) == 0:

            return None

        # Use largest face
        largest_face = max(

            faces,

            key=lambda f: f[2] * f[3]
        )

        fx, fy, fw, fh = largest_face

        face_crop = person_crop[
            fy:fy+fh,
            fx:fx+fw
        ]

        if face_crop.size == 0:

            return None

        analysis = self.deepface.analyze_face(
            face_crop
        )

        if analysis:

            analysis["track_id"] = track_id

            # Convert ROI coords to full frame
            analysis["bbox"] = (

                x1 + fx,
                y1 + fy,
                fw,
                fh
            )

            return analysis

        return None