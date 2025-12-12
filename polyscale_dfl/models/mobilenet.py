import torchvision.models as models
import torch.nn as nn

def MobileNetV2(pretrained=False, num_classes=10):
    model = models.mobilenet_v2(weights=None if not pretrained else models.MobileNet_V2_Weights.IMAGENET1K_V1)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    return model
