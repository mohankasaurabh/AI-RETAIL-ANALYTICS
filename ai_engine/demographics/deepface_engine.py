from deepface import DeepFace


class DeepFaceEngine:

    def analyze_face(self, face_crop):

        try:

            result = DeepFace.analyze(

                face_crop,

                actions=[
                    "age",
                    "gender"
                ],

                enforce_detection=False,

                detector_backend="opencv"
            )

            return {

                "age":
                    result[0]["age"],

                "gender":
                    result[0]["dominant_gender"]
            }

        except Exception as e:

            print(
                f"[ERROR] DeepFace: {e}"
            )

            return None