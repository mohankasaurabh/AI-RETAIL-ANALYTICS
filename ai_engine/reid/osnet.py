import cv2
import torch
import torchreid
import numpy as np
from torchvision import transforms


class OSNetFeatureExtractor:

    def __init__(self):

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model = (
            torchreid.models.build_model(
                name="osnet_x0_25",
                num_classes=1000,
                pretrained=True
            )
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        self.transform = transforms.Compose([

            transforms.ToPILImage(),

            transforms.Resize(
                (256, 128)
            ),

            transforms.ToTensor(),

            transforms.Normalize(

                mean=[
                    0.485,
                    0.456,
                    0.406
                ],

                std=[
                    0.229,
                    0.224,
                    0.225
                ]
            )
        ])

    # =====================================
    # FEATURE EXTRACTION
    # =====================================

    def extract(
        self,
        crop
    ):

        try:

            if crop is None:

                return None

            if crop.size == 0:

                return None

            crop = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2RGB
            )

            tensor = (
                self.transform(crop)
                .unsqueeze(0)
                .to(self.device)
            )

            with torch.no_grad():

                features = (
                    self.model(tensor)
                )

            features = (
                features
                .cpu()
                .numpy()
                .flatten()
            )

            return features

        except Exception as e:

            print(
                f"[OSNET ERROR] {e}"
            )

            return None