"""
ClientNode encapsulates the lifecycle & logic of a federated client:
- initialization with model + dataset
- local training, DP/MPC/Masking
- networking hooks to send updates to aggregator (via configured network API)
- ledger / chain hooks to register, stake, submit CIDs

This implementation focuses on clean interfaces: networking and chain clients are injected dependencies.
"""

from typing import Dict, Any, Optional, Callable
import numpy as np
import threading
import time
import json
import os
from .trainer import Trainer
from .dp import apply_dp_to_update
from .mpc import SecureClientAPI
from ..ipfs.ipfs_client import IPFSClient  # will exist in another module (stubbed here)
# networking client should implement send(to, payload) and broadcast(payload)
# chain client should implement register_client, submit_model_cid, reward

DEFAULT_MAX_NORM = 1.0

class ClientNode:
    def __init__(self,
                 client_id: str,
                 model_cfg: Dict[str, Any],
                 dataset: Dict[str, np.ndarray],
                 network_client,
                 chain_client,
                 ipfs_client: Optional[IPFSClient] = None,
                 dp_max_norm: float = DEFAULT_MAX_NORM,
                 dp_sigma: float = 0.0,
                 use_mpc: bool = False,
                 seed: Optional[int] = None):
        self.client_id = client_id
        self.model_cfg = model_cfg
        self.dataset = dataset
        self.network = network_client
        self.chain = chain_client
        self.ipfs = ipfs_client
        self.dp_max_norm = dp_max_norm
        self.dp_sigma = dp_sigma
        self.use_mpc = use_mpc
        self.seed = seed or int.from_bytes(client_id.encode("utf-8")[:4], "little", signed=False)
        self.trainer = Trainer(model_cfg)
        self.sec_api = SecureClientAPI(client_id, master_seed=(b"master_seed_" + str(self.seed).encode()))
        self._running = False
        self._thread = None
        # local state cache
        self.cached_state = self.trainer.get_state()

    def start_background(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _background_loop(self):
        # Example background job that reports periodically to network
        while self._running:
            try:
                stats = {"type": "heartbeat", "client": self.client_id, "ts": time.time()}
                self.network.broadcast(stats)
            except Exception:
                pass
            time.sleep(5.0)

    def apply_global_model(self, global_state: Dict[str, np.ndarray]):
        self.trainer.set_state(global_state)
        self.cached_state = global_state

    def local_train_and_prepare_update(self, epochs: int = 1, batch_size: int = 32, callback: Optional[Callable] = None) -> Dict[str, Any]:
        X = self.dataset["X_train"]
        y = self.dataset["y_train"]
        metrics = self.trainer.train(X, y, epochs=epochs, batch_size=batch_size, callbacks=callback)
        new_state = self.trainer.get_state()
        # compute delta
        delta = {}
        for k, v in new_state.items():
            delta[k] = (v.astype(np.float32) - self.cached_state[k].astype(np.float32))
        # apply DP
        if self.dp_sigma > 0:
            delta = apply_dp_to_update(delta, max_norm=self.dp_max_norm, sigma=self.dp_sigma, rng=np.random.RandomState(self.seed))
        # apply MPC mask if required
        if self.use_mpc:
            # For demo: create pairwise secrets assuming network knows peers to talk to
            peers = self.network.get_peers() if hasattr(self.network, "get_peers") else []
            pairwise = {}
            for p in peers:
                if p == self.client_id:
                    continue
                pairwise[p] = self.sec_api.create_pairwise_secret(p)
            masked, meta = self.sec_api.compute_masked_update(delta, pairwise)
            payload = {"type": "masked_update", "from": self.client_id, "masked": _to_serializable(masked), "meta": meta}
            self.network.send_to_aggregator(payload)
            # keep local mask info if needed
            return {"masked": masked, "meta": meta, "metrics": metrics}
        else:
            payload = {"type": "update", "from": self.client_id, "update": _to_serializable(delta)}
            self.network.send_to_aggregator(payload)
            return {"update": delta, "metrics": metrics}

    def publish_model_to_ipfs(self):
        state = self.trainer.get_state()
        if self.ipfs is None:
            raise RuntimeError("IPFS client not configured")
        cid = self.ipfs.add_state(state)
        # optionally register on chain
        if self.chain:
            self.chain.submit_model_cid(self.client_id, cid)
        return cid

def _to_serializable(d: Dict[str, np.ndarray]):
    return {k: v.tolist() for k, v in d.items()}
