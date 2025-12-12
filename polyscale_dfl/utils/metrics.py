import torch
import torch.nn as nn

def compute_accuracy(model, data_loader, device="cpu"):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in data_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x)
            correct += (pred.argmax(dim=1) == y).sum().item()
            total += y.size(0)
    return correct / total

def compute_loss(model, data_loader, device="cpu"):
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    count = 0
    with torch.no_grad():
        for x, y in data_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x)
            total_loss += criterion(pred, y).item()
            count += 1
    return total_loss / count
