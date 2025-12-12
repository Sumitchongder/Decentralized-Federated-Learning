"""
AggregatorNode

Responsibilities:
- Accept updates from clients (via networking abstraction)
- Optionally perform secure aggregation using secure_agg backend (stubbed / pluggable)
- Aggregate updates (FedAvg, FedProx)
- Version and store global models in IPFS
- Emit on-chain events via chain client
- Provide simple metrics for monitoring (round, participants, val metrics)
"""

from typing import Dict, Any, List, Optional, Callable
import threading
import time
import logging
import numpy as np
from collections import defaultdict
from ..ipfs.ipfs_client import IPFSClient
from ..chain.chain_stub import ChainStub  # pluggable with web3_client
from ..secure_agg import bonawitz as bonawitz_module  # if present, otherwise stub exists
from ..networking.p2p_stub import P2PStub

log = logging.getLogger("polyscale_fl.aggregator.aggregator_node")
logging.basicConfig(level=logging.INFO)

class AggregatorNode:
    def __init__(self,
                 aggregator_id: str = "aggregator_0",
                 model_cfg: Dict[str, Any] = None,
                 p2p_client: Optional[P2PStub] = None,
                 chain_client: Optional[ChainStub] = None,
                 ipfs_client: Optional[IPFSClient] = None,
                 secure_agg_backend: Optional[Any] = None,
                 aggregation_method: str = "fedavg"):
        self.aggregator_id = aggregator_id
        self.model_cfg = model_cfg or {"input_dim": 20, "hidden_dim": 64, "output_dim": 2}
        self.p2p = p2p_client or P2PStub()
        self.chain = chain_client or ChainStub()
        self.ipfs = ipfs_client or IPFSClient()
        self.secure_agg = secure_agg_backend  # expected interface: prepare_round, submit_mask, finalize
        self.aggregation_method = aggregation_method
        self._lock = threading.Lock()
        # internal buffers
        self._buffered_updates: List[Dict[str, Any]] = []
        self._buffered_masked: List[Dict[str, Any]] = []
        self._buffered_masks: List[Dict[str, Any]] = []
        self._round = 0
        # initialize a global model state as small random dict
        self.global_state = self._init_global_state()
        self.history = {"round": [], "val_loss": [], "val_acc": [], "participants": []}
        # register as a P2P node
        try:
            self.p2p.register(self.aggregator_id, self._on_message)
            self.p2p.set_aggregator(self.aggregator_id)
        except Exception:
            # some p2p clients may not implement register
            pass

    def _init_global_state(self):
        # create a deterministic small zeroed model state dict (numpy arrays)
        # Shape decisions follow model_cfg; keys mimic torch naming for consistency
        in_dim = self.model_cfg.get("input_dim", 20)
        h = self.model_cfg.get("hidden_dim", 64)
        out = self.model_cfg.get("output_dim", 2)
        return {
            "W1": np.zeros((in_dim, h), dtype=np.float32),
            "b1": np.zeros((h,), dtype=np.float32),
            "W2": np.zeros((h, out), dtype=np.float32),
            "b2": np.zeros((out,), dtype=np.float32)
        }

    # ------------ Message handling ------------
    def _on_message(self, from_id: str, message: Dict[str, Any]):
        """
        Expected message forms:
        - {"type":"update", "from":client_id, "update": {param_name: list_or_array}}
        - {"type":"masked_update", "from":client_id, "masked": {...}}
        - {"type":"mask_share", "from":client_id, "mask": {...}}
        - {"type":"heartbeat", ...}
        """
        try:
            t = message.get("type")
            if t == "update":
                upd = self._to_numpy_state(message["update"])
                with self._lock:
                    self._buffered_updates.append({"from": from_id, "update": upd})
            elif t == "masked_update":
                masked = self._to_numpy_state(message["masked"])
                with self._lock:
                    self._buffered_masked.append({"from": from_id, "masked": masked})
            elif t == "mask_share":
                mask = self._to_numpy_state(message["mask"])
                with self._lock:
                    self._buffered_masks.append({"from": from_id, "mask": mask})
            elif t == "heartbeat":
                # ignore or log
                log.debug("heartbeat from %s", from_id)
            else:
                log.debug("unknown message type from %s: %s", from_id, t)
        except Exception as e:
            log.exception("error handling message from %s: %s", from_id, e)

    def _to_numpy_state(self, obj: Dict[str, Any]) -> Dict[str, np.ndarray]:
        out = {}
        for k, v in obj.items():
            out[k] = np.array(v, dtype=np.float32)
        return out

    # ------------ Aggregation ------------
    def collect_and_aggregate(self, secure_agg: bool = False, min_participants: Optional[int] = None):
        """
        Aggregate whatever updates the aggregator has collected so far.
        If secure_agg=True we will attempt to use secure_agg backend which expects:
            prepare_round(client_ids)
            submit_mask(client_id, mask)
            unmask_sum(total_mask)
        For backward compatibility the aggregator will also accept raw updates (non-secure).
        """
        with self._lock:
            num_updates = len(self._buffered_updates)
            num_masked = len(self._buffered_masked)
            num_masks = len(self._buffered_masks)

            # decide which path to use
            if secure_agg and num_masked > 0 and num_masks >= num_masked:
                # simplified: sum masked updates and subtract masks
                sum_masked = self._sum_state_dicts([m["masked"] for m in self._buffered_masked])
                sum_masks = self._sum_state_dicts([m["mask"] for m in self._buffered_masks])
                aggregate = {}
                n = max(1, num_masked)
                for k in sum_masked.keys():
                    aggregate[k] = (sum_masked[k] - sum_masks.get(k, 0.0)) / float(n)
                participants = [m["from"] for m in self._buffered_masked]
                # clear
                self._buffered_masked.clear()
                self._buffered_masks.clear()
            elif num_updates > 0:
                # perform FedAvg
                updates = [u["update"] for u in self._buffered_updates]
                participants = [u["from"] for u in self._buffered_updates]
                aggregate = self._average_state_dicts(updates)
                # clear
                self._buffered_updates.clear()
            else:
                return None

        # apply aggregate to global_state
        with self._lock:
            for k, v in aggregate.items():
                self.global_state[k] = (self.global_state[k].astype(np.float32) + v.astype(np.float32)).astype(np.float32)
            self._round += 1
            round_no = self._round

        # snapshot model to IPFS and publish to chain
        cid = self._snapshot_to_ipfs(self.global_state)
        try:
            metrics = {"dummy": 0.0}
            self.chain.register_model(cid, round_no, metrics)
        except Exception:
            log.debug("chain client publish failed (chain may be stub)")

        # record history
        self.history["round"].append(round_no)
        self.history["participants"].append(len(participants))
        self.history["val_loss"].append(None)
        self.history["val_acc"].append(None)

        log.info("Aggregated round %d | participants=%d | cid=%s", round_no, len(participants), cid)
        return {"round": round_no, "cid": cid, "participants": participants}

    def _average_state_dicts(self, list_of_states: List[Dict[str, np.ndarray]]):
        if not list_of_states:
            return {}
        n = len(list_of_states)
        avg = {}
        keys = list_of_states[0].keys()
        for k in keys:
            accum = None
            for s in list_of_states:
                if accum is None:
                    accum = s[k].astype(np.float64) / float(n)
                else:
                    accum += s[k].astype(np.float64) / float(n)
            avg[k] = accum.astype(np.float32)
        return avg

    def _sum_state_dicts(self, list_of_states: List[Dict[str, np.ndarray]]):
        if not list_of_states:
            return {}
        ssum = {}
        for s in list_of_states:
            for k, v in s.items():
                ssum.setdefault(k, np.zeros_like(v, dtype=np.float32))
                ssum[k] = ssum[k] + v.astype(np.float32)
        return ssum

    def _snapshot_to_ipfs(self, state: Dict[str, np.ndarray]) -> str:
        # store via IPFS client wrapper
        try:
            cid = self.ipfs.add_state(state)
            return cid
        except Exception as e:
            log.exception("ipfs snapshot failed: %s", e)
            # fallback: write to disk and return sha256 hex
            import json, hashlib
            b = json.dumps({k: v.tolist() for k, v in state.items()}).encode("utf-8")
            return hashlib.sha256(b).hexdigest()

    # ------------ Utilities ------------
    def get_global_state(self) -> Dict[str, np.ndarray]:
        with self._lock:
            return {k: v.copy() for k, v in self.global_state.items()}

    def get_history(self) -> Dict[str, List]:
        return dict(self.history)
