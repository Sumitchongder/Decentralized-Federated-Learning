import torchvision.models as models
import torch.nn as nn

def VisionTransformer(pretrained=False, num_classes=10):
    model = models.vit_b_16(weights=None if not pretrained else models.ViT_B_16_Weights.IMAGENET1K_V1)
    model.heads.head = nn.Linear(model.heads.head.in_features, num_classes)
    return model
