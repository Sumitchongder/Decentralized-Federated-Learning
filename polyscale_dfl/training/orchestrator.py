from aggregator.aggregator_node import AggregatorNode
from secure_agg.bonawitz import SecureAggregator

class TrainingOrchestrator:
    """
    Orchestrates federated learning rounds with secure aggregation
    """
    def __init__(self, aggregator: AggregatorNode, clients, rounds=5):
        self.aggregator = aggregator
        self.clients = clients
        self.rounds = rounds
        self.secagg = SecureAggregator()
        self.history = []

    def run(self, epochs_per_round=1):
        for r in range(1, self.rounds + 1):
            print(f"=== Starting Round {r} ===")
            # Train clients
            client_updates = [c.train_one_round(epochs_per_round) for c in self.clients]
            # Secure aggregation
            aggregated_update = self.secagg.aggregate(client_updates)
            # Update global model
            acc = self.aggregator.aggregate_round([aggregated_update])
            self.history.append({"round": r, "accuracy": acc})
        return self.history
