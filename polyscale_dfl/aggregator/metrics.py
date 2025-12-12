import torch
import torch.nn as nn

class EvaluationMetrics:
    def __init__(self):
        self.loss_fn = nn.CrossEntropyLoss()

    def evaluate(self, model, test_loader, device="cpu"):
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(device), y.to(device)
                pred = model(x)
                correct += (pred.argmax(dim=1) == y).sum().item()
                total += y.size(0)
        return correct / total
