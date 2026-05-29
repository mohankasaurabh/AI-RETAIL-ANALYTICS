import cv2
import torch
import torchvision.transforms as transforms

from PIL import Image

from ai_engine.reid.osnet import OSNetReID


class FeatureExtractor:

    def __init__(self):

        self.model = OSNetReID().get_model()

        self.transform = transforms.Compose([
            transforms.Resize((256, 128)),
            transforms.ToTensor(),
        ])

    def extract(self, frame, bbox):

        x1, y1, x2, y2 = bbox

        crop = frame[y1:y2, x1:x2]

        if crop.size == 0:
            return None

        image = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(image)

        tensor = self.transform(image)

        tensor = tensor.unsqueeze(0)

        with torch.no_grad():

            features = self.model(tensor)

        return features.numpy()