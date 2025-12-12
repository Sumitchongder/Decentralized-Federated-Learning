"""
MPC / Secure Aggregation stubs and helpers.

This module defines the interface the aggregator expects, and basic helper utilities
for pairwise mask generation. It intentionally does NOT implement a full Bonawitz
protocol here — instead it provides clean extension points where a proper Bonawitz
implementation (or a PySyft / MP-SPDZ backend) can be wired.

Provided classes:
- MaskManager: generates pseudo-random masks deterministically from seeds (useful for tests)
- SecureClientAPI: small client-side facade for key exchange / mask commitments
- SecureAggregatorAPI: aggregator-side facade to reconstruct masks and unmask
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import hashlib
import hmac

class MaskManager:
    """
    Deterministic mask generation using HMAC-SHA256 for reproducibility in tests.
    NOTE: Not cryptographically equivalent to Bonawitz; replace with full protocol for production.
    """
    def __init__(self, seed_bytes: bytes):
        self.seed = seed_bytes

    def generate_mask(self, key: bytes, shape):
        """
        key: bytes key (could be pairwise shared secret)
        shape: desired numpy shape
        returns: numpy array mask
        """
        out = np.zeros(shape, dtype=np.float32)
        # create deterministic stream from HMAC
        block = 0
        total = int(np.prod(shape))
        idx = 0
        while idx < total:
            h = hmac.new(self.seed, key + block.to_bytes(4, "big"), digestmod=hashlib.sha256).digest()
            # convert bytes to float32 numbers via int conversion
            for j in range(0, len(h), 4):
                if idx >= total:
                    break
                val = int.from_bytes(h[j:j+4], "big", signed=False)
                # map int -> float in small range
                out.flat[idx] = ((val % 1000) - 500) / 1e5
                idx += 1
            block += 1
        return out.reshape(shape)

class SecureClientAPI:
    """
    Client-side secure aggregation facade (simplified).
    Methods:
      - create_pairwise_secret(peer_id) -> secret (bytes)
      - compute_masked_update(update, pairwise_secrets) -> masked_update, mask_meta
    """
    def __init__(self, client_id: str, master_seed: bytes = b"default_seed"):
        self.client_id = client_id.encode()
        self.master = master_seed
        self.mask_manager = MaskManager(self.master)

    def create_pairwise_secret(self, peer_id: str) -> bytes:
        # In practice this would be ECDH shared secret or KDF of keys.
        # Here we synthesize deterministically for testing.
        info = self.client_id + b"::" + peer_id.encode()
        secret = hashlib.sha256(self.master + info).digest()
        return secret

    def compute_masked_update(self, update: Dict[str, np.ndarray], pairwise_secrets: Dict[str, bytes]) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Apply pairwise masks using provided secrets.
        Returns masked_update and mask_meta (which includes info aggregator can use to reconstruct later).
        """
        masked = {}
        masks_used = {}
        for k, v in update.items():
            arr = v.astype(np.float32)
            mask_sum = np.zeros_like(arr)
            for peer, secret in pairwise_secrets.items():
                m = self.mask_manager.generate_mask(secret, arr.shape)
                # convention: if peer id is lexicographically greater, subtract (to cancel later deterministically)
                if peer.encode() > self.client_id:
                    mask_sum += m
                else:
                    mask_sum -= m
            masked[k] = (arr + mask_sum).astype(np.float32)
        # mask_meta may contain nothing for this stub
        return masked, {"secrets_info": list(pairwise_secrets.keys())}

class SecureAggregatorAPI:
    """
    Aggregator-side helper to reconstruct sum of masks given pairwise secrets (for simplified protocol).
    In a real Bonawitz run, aggregator does not learn per-client secrets; instead the clients reveal mask sums
    or the protocol handles dropouts carefully. This is for local testing only.
    """
    def __init__(self, master_seed: bytes = b"default_seed"):
        self.master = master_seed
        self.mask_manager = MaskManager(self.master)

    def reconstruct_masks_sum(self, all_client_ids: List[str], secrets_map: Dict[Tuple[str, str], bytes], shape_example):
        """
        secrets_map: mapping (client_a, client_b) -> secret bytes (both orders possible)
        Returns: sum_masks (dict mapping param_name -> numpy array) assuming same shapes
        """
        # For the stub we simply iterate pairwise secrets and sum/cancel masks amortized.
        # Real protocol is far more subtle.
        sum_mask = np.zeros(shape_example, dtype=np.float32)
        for (a, b), secret in secrets_map.items():
            m = self.mask_manager.generate_mask(secret, shape_example)
            # decide sign deterministically
            if a.encode() > b.encode():
                sum_mask += m
            else:
                sum_mask -= m
        return sum_mask
