import pytest
import torch
from client.client_node import ClientNode
from models.cnn import SimpleCNN
from datasets.loader import load_mnist

@pytest.fixture
def client():
    train_loaders, _ = load_mnist(num_clients=1, batch_size=32)
    model = SimpleCNN()
    return ClientNode(id=0, model=model, train_loader=train_loaders[0])

def test_client_training(client):
    update = client.train_one_round(epochs=1)
    assert isinstance(update, dict)
    assert all(isinstance(v, torch.Tensor) for v in update.values())
