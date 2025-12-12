"""
Scheduler: Controls round timing and client selection policy.

Features:
- Synchronous rounds with fixed timeout
- Asynchronous collection with sliding window
- Pluggable selection strategy (random, round-robin, reputation-weighted)
- Works with AggregatorNode and networking layer to instruct clients to start a round
"""

from typing import List, Optional, Callable, Dict, Any
import random
import threading
import time
import logging

log = logging.getLogger("polyscale_fl.aggregator.scheduler")
logging.basicConfig(level=logging.INFO)

class Scheduler:
    def __init__(self, aggregator_node, p2p_client, client_list: List[str],
                 round_timeout: float = 10.0, clients_per_round: Optional[int] = None,
                 selection_strategy: str = "random"):
        self.aggregator = aggregator_node
        self.p2p = p2p_client
        self.clients = client_list[:]
        self.clients_per_round = clients_per_round or max(1, len(self.clients))
        self.round_timeout = round_timeout
        self.selection_strategy = selection_strategy
        self._running = False
        self._thread = None

    def _select_clients(self) -> List[str]:
        if self.selection_strategy == "random":
            return random.sample(self.clients, min(self.clients_per_round, len(self.clients)))
        elif self.selection_strategy == "round_robin":
            # simple rotating selection
            sel = []
            for _ in range(self.clients_per_round):
                sel.append(self.clients.pop(0))
                self.clients.append(sel[-1])
            return sel
        else:
            # default to random
            return random.sample(self.clients, min(self.clients_per_round, len(self.clients)))

    def start_rounds(self, rounds: int = 10, secure_agg: bool = False):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, args=(rounds, secure_agg), daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _run_loop(self, rounds: int, secure_agg: bool):
        for r in range(rounds):
            if not self._running:
                break
            selected = self._select_clients()
            log.info("Starting round %d | selected_clients=%s", r+1, selected)
            # send start message to clients (they must be listening)
            for c in selected:
                try:
                    self.p2p.send(self.aggregator.aggregator_id, c, {"type": "start_round", "round": r+1, "aggregator": self.aggregator.aggregator_id})
                except Exception:
                    pass
            # wait timeout for clients to send updates
            time.sleep(self.round_timeout)
            # collect and aggregate
            res = self.aggregator.collect_and_aggregate(secure_agg=secure_agg, min_participants=len(selected))
            if res is None:
                log.info("No updates collected in round %d", r+1)
            else:
                log.info("Round %d aggregated. CID: %s", r+1, res["cid"])
        log.info("Scheduler finished rounds")
        self._running = False
