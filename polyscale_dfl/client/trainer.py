import torch
import torch.nn as nn
import torch.optim as optim

def train_one_round(model, train_loader, epochs=1, device="cpu"):
    model.train()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    for _ in range(epochs):
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()
    # Return weight difference
    return {k: v.clone().detach() for k, v in model.state_dict().items()}
