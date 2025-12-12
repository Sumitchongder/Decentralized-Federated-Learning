import torch
from torch.utils.data import TensorDataset

def generate_synthetic(num_clients=2, num_samples=100, input_dim=10, num_classes=2):
    clients_data = []
    for _ in range(num_clients):
        X = torch.randn(num_samples, input_dim)
        y = torch.randint(0, num_classes, (num_samples,))
        clients_data.append(TensorDataset(X, y))
    return clients_data
