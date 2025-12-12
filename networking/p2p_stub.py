"""
P2PStub: In-process P2P-like bus for local development and unit tests.

- Registers nodes (client ids and callbacks)
- Supports send, broadcast, and a simple 'aggregator' concept
- Thread-safe
- Suitable for playground (docker-compose) where we launch multiple Python processes that connect
  via a minimal HTTP RPC or shared Redis — for pure single-process demos this is sufficient.

Usage:
    bus = P2PStub()
    bus.register("aggregator", aggregator_callback)
    bus.register("client_1", client_callback)
    bus.send("client_1", "aggregator", {"type": "update", ...})
"""

from typing import Callable, Dict, List, Any, Optional
import threading
import time
import json
import random

class P2PStub:
    def __init__(self, latency_mean: float = 0.02, latency_jitter: float = 0.01):
        self._nodes: Dict[str, Callable[[str, dict], None]] = {}
        self._lock = threading.Lock()
        self.latency_mean = latency_mean
        self.latency_jitter = latency_jitter
        self.aggregator_id: Optional[str] = None

    def register(self, node_id: str, handler: Callable[[str, dict], None]):
        with self._lock:
            self._nodes[node_id] = handler

    def unregister(self, node_id: str):
        with self._lock:
            if node_id in self._nodes:
                del self._nodes[node_id]

    def set_aggregator(self, aggregator_id: str):
        self.aggregator_id = aggregator_id

    def get_peers(self) -> List[str]:
        with self._lock:
            return list(self._nodes.keys())

    def send(self, from_id: str, to_id: str, payload: dict):
        # deliver in background thread to simulate network latency
        def deliver():
            delay = max(0.0, random.gauss(self.latency_mean, self.latency_jitter))
            time.sleep(delay)
            handler = None
            with self._lock:
                handler = self._nodes.get(to_id)
            if handler:
                try:
                    handler(from_id, payload)
                except Exception as e:
                    print(f"[p2p_stub] handler error delivering to {to_id}: {e}")
        t = threading.Thread(target=deliver, daemon=True)
        t.start()

    def broadcast(self, from_id: str, payload: dict):
        with self._lock:
            peers = list(self._nodes.items())
        for peer_id, handler in peers:
            if peer_id == from_id:
                continue
            self.send(from_id, peer_id, payload)

    # Convenience wrapper used in client.cli
    def send_to_aggregator(self, from_id: str, payload: dict):
        if self.aggregator_id is None:
            raise RuntimeError("Aggregator not set in P2PStub")
        self.send(from_id, self.aggregator_id, payload)
