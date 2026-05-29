from ultralytics import YOLO
import torch


class YOLOLoader:

    def __init__(self, model_path="yolo11s.pt"):

        self.device = "mps" if torch.backends.mps.is_available() else "cpu"

        print(f"[INFO] Using Device: {self.device}")

        self.model = YOLO(model_path)

        self.model.to(self.device)

    def get_model(self):

        return self.model