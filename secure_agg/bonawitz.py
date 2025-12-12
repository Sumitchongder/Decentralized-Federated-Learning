"""
Simplified Bonawitz-style secure aggregation implementation.

Main classes:
- BonawitzClient: client-side helper
- BonawitzAggregator: aggregator-side helper

Protocol sketch (simplified):
1. Client -> Aggregator: publish(public_key)
2. Aggregator -> Clients: list of all public_keys (or clients can fetch)
3. Each client computes pairwise shared secrets with peers using X25519(priv_i, pub_j)
4. Each client derives pairwise masks via HKDF(shared_secret || "mask" || param_index)
   and sums them (with deterministic sign rule) into a per-parameter mask
5. Client sends masked_update = local_update + mask to Aggregator
6. Aggregator sums masked_updates; clients later send masks (or mask-shares) to allow unmasking.
   (In production this step uses verifiable secret-sharing to handle dropouts.)

Interfaces provided:
- BonawitzClient.create_keypair()
- BonawitzClient.public_bytes()
- BonawitzClient.compute_pairwise_mask(peer_pub_bytes, shape_map)
- BonawitzClient.create_masked_update(local_update, peers_pubmap)
- BonawitzAggregator.collect_public_key(client_id, pub_bytes)
- BonawitzAggregator.collect_masked_update(client_id, masked_update)
- BonawitzAggregator.request_unmasking() -> collects masks from clients and unmask sum

Notes:
- Uses cryptography.hazmat.primitives.asymmetric.x25519
- Uses HKDF-SHA256 for PRG expansion
"""

from typing import Dict, Tuple, List, Any
import os
import base64
import json
import hashlib
import threading
import logging

import numpy as np

# Crypto imports (cryptography)
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from .utils import flatten_state_shapes, prg_bytes_to_state, state_to_bytes, add_state_dicts, sub_state_dicts

log = logging.getLogger("polyscale_fl.secure_agg.bonawitz")
logging.basicConfig(level=logging.INFO)

# ---------- Helpers ----------
def hkdf_expand(secret: bytes, info: bytes, length: int = 1024) -> bytes:
    """
    Expand ECDH shared secret into `length` bytes deterministically using HKDF-SHA256.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=info,
    )
    return hkdf.derive(secret)

def generate_mask_from_shared_secret(shared_secret: bytes, shapes: List[Tuple[str, Tuple[int, ...]]]) -> Dict[str, np.ndarray]:
    """
    Derive enough PRG bytes and convert to state dict matching shapes.
    The info parameter should include a context string to avoid key reuse.
    """
    # estimate required number of floats
    total_floats = sum(int(np.prod(s)) for (_, s) in shapes)
    required_bytes = total_floats * 4
    # HKDF length rounding: choose at least required_bytes (plus some headroom)
    length = max(required_bytes, 1024)
    info = b"polyscale-secagg-mask"
    prg = hkdf_expand(shared_secret, info=info, length=length)
    return prg_bytes_to_state(prg, shapes)


# ---------- Client-side protocol ----------
class BonawitzClient:
    def __init__(self, client_id: str, master_seed: bytes = None):
        self.client_id = client_id
        self._priv: X25519PrivateKey = None
        self._pub: X25519PublicKey = None
        # optionally deterministic seed for tests
        self.master_seed = master_seed or os.urandom(16)
        # store peers' public keys if provided
        self.peers_pub: Dict[str, bytes] = {}  # client_id -> public bytes
        self.shapes_cache: List[Tuple[str, Tuple[int, ...]]] = []
        # store local pairwise masks (keyed by peer id) for potential reveal
        self._pairwise_masks: Dict[str, Dict[str, np.ndarray]] = {}

    def create_keypair(self):
        self._priv = X25519PrivateKey.generate()
        self._pub = self._priv.public_key()
        return self._pub_bytes()

    def _pub_bytes(self) -> bytes:
        if self._pub is None:
            return b""
        return self._pub.public_bytes()

    def public_bytes(self) -> str:
        """Return base64-encoded public key for easy transfer."""
        return base64.b64encode(self._pub_bytes()).decode("ascii")

    def load_peers_public_map(self, peers_map: Dict[str, str]):
        """
        peers_map: client_id -> base64(pub_bytes)
        """
        self.peers_pub = {cid: base64.b64decode(b64) for cid, b64 in peers_map.items() if cid != self.client_id}

    def compute_pairwise_mask(self, peer_id: str, peer_pub_bytes: bytes, shapes):
        """
        Compute the pairwise mask with one peer (returns numpy state dict).
        Stores mask internally for later reveal if needed.
        """
        if self._priv is None:
            raise RuntimeError("Keypair not created")
        peer_pub = X25519PublicKey.from_public_bytes(peer_pub_bytes)
        shared = self._priv.exchange(peer_pub)  # raw shared secret bytes
        # derive a mask using HKDF and the state shapes (deterministic)
        mask_state = generate_mask_from_shared_secret(shared, shapes)
        # Conventions: to cancel masks later, we need deterministic sign rule between pair:
        # If client_id < peer_id lexicographically, client will add mask, else subtract mask.
        # To keep sign consistent across peers, we store mask as-is; aggregator will know sign rule.
        self._pairwise_masks[peer_id] = mask_state
        return mask_state

    def create_masked_update(self, local_update: Dict[str, np.ndarray], peers_pubmap: Dict[str, str]) -> Dict[str, Any]:
        """
        Given a local_update (state-dict of numpy arrays), compute pairwise masks against each peer
        and return the masked_update to send to aggregator.

        Returns:
            {
                "client_id": str,
                "masked_update": {k: list},  # numpy arrays converted to lists for JSON
                "meta": {"pub": base64(pub_bytes), "peers": {peer_id: base64(pub)}}
            }
        """
        # cache shapes
        shapes_list, total = flatten_state_shapes(local_update)
        self.shapes_cache = shapes_list
        # ensure keypair exists
        if self._priv is None:
            self.create_keypair()
        # load peers
        self.load_peers_public_map(peers_pubmap)
        # start with delta (local_update)
        acc = {k: local_update[k].astype(np.float32).copy() for k in local_update}
        # for each peer compute mask and add/subtract according to deterministic sign rule
        for peer_id, pub_b64 in peers_pubmap.items():
            if peer_id == self.client_id:
                continue
            peer_pub_bytes = base64.b64decode(pub_b64)
            mask = self.compute_pairwise_mask(peer_id, peer_pub_bytes, shapes_list)
            # decide sign: client adds mask if client_id < peer_id else subtract
            if self.client_id < peer_id:
                acc = add_state_dicts(acc, mask)
            else:
                acc = sub_state_dicts(acc, mask)
        # convert to lists for JSON transport
        serial = {k: v.tolist() for k, v in acc.items()}
        return {"client_id": self.client_id, "masked_update": serial, "meta": {"pub": self.public_bytes(), "peers": peers_pubmap}}

    def export_mask_for_aggregator(self, peer_id: str):
        """
        Export pairwise mask with a peer to give to aggregator for unmasking.
        In a real Bonawitz protocol this would be performed via secret-sharing or
        secure channels with commitments verifying correctness.

        Returns: dict mapping param name -> list
        """
        m = self._pairwise_masks.get(peer_id)
        if m is None:
            raise RuntimeError("No pairwise mask for peer %s" % peer_id)
        return {k: v.tolist() for k, v in m.items()}


# ---------- Aggregator-side protocol ----------
class BonawitzAggregator:
    def __init__(self):
        # store client public keys
        self.pubkeys: Dict[str, bytes] = {}
        # store received masked updates
        self.masked_updates: Dict[str, Dict[str, Any]] = {}
        # store masks received (from clients revealing them)
        self.revealed_masks: Dict[Tuple[str, str], Dict[str, List]] = {}  # (a,b) -> mask dict
        self._lock = threading.Lock()
        # cached shapes (inferred from first masked update)
        self.shapes = None

    def collect_public_key(self, client_id: str, pub_b64: str):
        with self._lock:
            self.pubkeys[client_id] = base64.b64decode(pub_b64)

    def collect_masked_update(self, client_id: str, masked_update_obj: Dict[str, Any]):
        """
        masked_update_obj = {"masked_update": {k: list}, "meta": {...}}
        """
        with self._lock:
            self.masked_updates[client_id] = masked_update_obj["masked_update"]
            if self.shapes is None:
                # infer shapes
                import numpy as _np
                shapes = []
                for k, v in masked_update_obj["masked_update"].items():
                    arr = _np.array(v, dtype=_np.float32)
                    shapes.append((k, arr.shape))
                self.shapes = shapes

    def request_masks_from_clients(self, clients: List[str]) -> List[str]:
        """
        In real Bonawitz aggregator instructs clients to reveal additive shares if needed.
        Here we return the list of clients the aggregator expects masks from (simple policy).
        Note: actual exchange must be performed via P2P channels; this method just returns who must send.
        """
        # Simplified: ask all clients to reveal pairwise masks
        return clients

    def receive_revealed_mask(self, from_client: str, peer_id: str, mask_obj: Dict[str, List]):
        """
        Clients will submit their pairwise mask for (from_client <-> peer_id) pair.
        Store under ordered tuple (min,max) for deterministic cancellation.
        """
        key = tuple(sorted([from_client, peer_id]))
        with self._lock:
            self.revealed_masks[key] = mask_obj

    def unmask_aggregate(self) -> Dict[str, Any]:
        """
        Compute sum(masked_updates) - sum(all pairwise masks) to recover sum of deltas.
        Assumes all relevant pairwise masks were revealed (simplified).
        Returns aggregated delta state dict (numpy arrays).
        """
        with self._lock:
            import numpy as _np
            # sum masked updates
            keys = list(self.masked_updates.keys())
            if not keys:
                return {}
            # convert masked updates to numpy arrays and sum
            sum_masked = {}
            for cid, m in self.masked_updates.items():
                for k, v in m.items():
                    arr = _np.array(v, dtype=_np.float32)
                    sum_masked.setdefault(k, _np.zeros_like(arr, dtype=_np.float32))
                    sum_masked[k] += arr
            # sum all revealed masks (pairwise)
            sum_masks = {}
            for (a, b), mask_obj in self.revealed_masks.items():
                for k, v in mask_obj.items():
                    arr = _np.array(v, dtype=_np.float32)
                    sum_masks.setdefault(k, _np.zeros_like(arr, dtype=_np.float32))
                    # Decide sign: when client with smaller id added mask, and larger subtracted, so combined contribution is zero.
                    # Since both sides revealed same mask, aggregator subtracts the mask once.
                    sum_masks[k] += arr
            # final aggregate = sum_masked - sum_masks
            aggregate = {}
            n = max(1, len(keys))
            for k, v in sum_masked.items():
                aggregate[k] = (v - sum_masks.get(k, 0.0)) / float(n)
            return aggregate
