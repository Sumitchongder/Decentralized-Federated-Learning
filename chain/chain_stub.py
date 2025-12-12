"""
ChainStub: Lightweight in-memory blockchain used for local demos.

Implements a reduced version of the ModelRegistry and RewardToken logic.

Clients use:
    chain_stub.register_model(cid, round, metrics)
    chain_stub.reward(node_id, amount)
"""

from typing import Dict, List, Any
import time
import threading

class ChainStub:
    def __init__(self):
        self._lock = threading.Lock()

        # Model entries stored as list
        self.models: List[Dict[str, Any]] = []

        # Token balances
        self.balances: Dict[str, float] = {}

        # Reputation scores
        self.reputation: Dict[str, float] = {}

    def register_model(self, cid: str, round_number: int, metrics: Dict[str, float]):
        """
        Simulates a ModelRegistry smart contract event.
        """
        with self._lock:
            entry = {
                "cid": cid,
                "round": round_number,
                "metrics": metrics,
                "timestamp": time.time()
            }
            self.models.append(entry)
            return entry

    def reward(self, node_id: str, amount: float):
        """
        Simulates a RewardToken transfer.
        """
        with self._lock:
            self.balances[node_id] = self.balances.get(node_id, 0.0) + amount
            return self.balances[node_id]

    def penalize(self, node_id: str, amount: float):
        """
        Decrease balance for malicious behavior.
        """
        with self._lock:
            self.balances[node_id] = self.balances.get(node_id, 0.0) - amount
            return self.balances[node_id]

    def set_reputation(self, node_id: str, score: float):
        with self._lock:
            self.reputation[node_id] = score

    def get_reputation(self, node_id: str) -> float:
        return self.reputation.get(node_id, 0.0)

    def get_models(self):
        return list(self.models)

    def get_balance(self, node_id: str):
        return self.balances.get(node_id, 0.0)
