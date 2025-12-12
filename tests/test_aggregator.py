import pytest
import torch
from models.cnn import SimpleCNN
from aggregator.server import Aggregator

def test_aggregator_update():
    model = SimpleCNN()
    aggregator = Aggregator(model=model)
    
    dummy_update = {k: torch.ones_like(v) for k, v in model.state_dict().items()}
    global_model = aggregator.update_global_model([dummy_update, dummy_update])
    
    for k, v in global_model.state_dict().items():
        assert torch.allclose(v, torch.ones_like(v))
