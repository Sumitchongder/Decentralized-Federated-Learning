import pytest
import torch
from client.client_node import ClientNode
from aggregator.server import Aggregator
from secure_agg.secagg import SecureAggregator
from models.cnn import SimpleCNN
from datasets.loader import load_mnist

@pytest.mark.slow
def test_full_fl_pipeline():
    # Load dataset
    train_loaders, test_loader = load_mnist(num_clients=2, batch_size=16)
    
    # Initialize clients
    clients = []
    for i in range(2):
        model = SimpleCNN()
        clients.append(ClientNode(id=i, model=model, train_loader=train_loaders[i]))
    
    # Local training
    updates = [c.train_one_round(epochs=1) for c in clients]
    
    # Secure aggregation
    secagg = SecureAggregator()
    aggregated = secagg.aggregate(updates)
    
    # Global model update
    aggregator = Aggregator(model=SimpleCNN())
    global_model = aggregator.update_global_model([aggregated])
    
    # Check global model weights exist
    assert all(isinstance(v, torch.Tensor) for v in global_model.state_dict().values())
