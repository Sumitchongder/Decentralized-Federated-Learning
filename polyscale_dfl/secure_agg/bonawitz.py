import torch
from .pairwise_masks import generate_pairwise_masks

class SecureAggregator:
    """
    Bonawitz-style secure aggregation for federated learning
    """
    def __init__(self):
        pass

    def aggregate(self, client_updates):
        """
        Aggregate updates securely using additive masks.
        client_updates: list of masked updates from clients
        """
        # Simple additive aggregation (masks already cancel out)
        agg = {}
        for k in client_updates[0]:
            agg[k] = sum([u[k] for u in client_updates]) / len(client_updates)
        return agg
