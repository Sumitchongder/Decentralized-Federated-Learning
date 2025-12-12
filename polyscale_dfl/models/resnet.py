import torchvision.models as models

def ResNet18(pretrained=False, num_classes=10):
    model = models.resnet18(weights=None if not pretrained else models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    return model
