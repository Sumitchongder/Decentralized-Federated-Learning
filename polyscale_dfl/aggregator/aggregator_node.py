import torch
from .model_avg import fed_avg
from .metrics import EvaluationMetrics

class AggregatorNode:
    def __init__(self, model, clients, test_loader=None):
        self.global_model = model
        self.clients = clients
        self.test_loader = test_loader
        self.metrics = EvaluationMetrics()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.global_model.to(self.device)

    def aggregate_round(self, client_updates):
        """
        Perform aggregation of client updates using FedAvg
        """
        self.global_model.load_state_dict(fed_avg(client_updates))
        if self.test_loader:
            acc = self.metrics.evaluate(self.global_model, self.test_loader, self.device)
            print(f"Round accuracy: {acc:.4f}")
            return acc
        return None
