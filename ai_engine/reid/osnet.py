import torchreid


class OSNetReID:

    def __init__(self):

        self.model = torchreid.models.build_model(
            name="osnet_x0_25",
            num_classes=1000,
            pretrained=True
        )

        self.model.eval()

    def get_model(self):

        return self.model