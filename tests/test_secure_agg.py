import pytest
import torch
from secure_agg.secagg import SecureAggregator

def test_secure_aggregation():
    secagg = SecureAggregator()
    dummy_updates = [
        {"w": torch.tensor([1.0, 2.0])},
        {"w": torch.tensor([3.0, 4.0])}
    ]
    aggregated = secagg.aggregate(dummy_updates)
    assert torch.allclose(aggregated["w"], torch.tensor([2.0, 3.0]))
