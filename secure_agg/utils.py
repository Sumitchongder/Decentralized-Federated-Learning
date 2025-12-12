"""
Utilities for secure_agg module:
- deterministic PRG: expand shared secret -> bytes -> float32 mask arrays
- serialization helpers for model state dicts (numpy arrays)
- shape flattening / reconstitution helpers
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import math
import json

def flatten_state_shapes(state: Dict[str, np.ndarray]) -> Tuple[List[Tuple[str, Tuple[int, ...]]], int]:
    """
    Return list of (key, shape) and total number of floats when flattened.
    """
    items = []
    total = 0
    for k, v in state.items():
        shape = tuple(v.shape)
        items.append((k, shape))
        total += int(np.prod(shape))
    return items, total

def state_to_bytes(state: Dict[str, np.ndarray]) -> bytes:
    """
    Convert a state dict to a deterministic bytes-sequence for hashing / commitment.
    (Used for commitments only — not for PRG)
    """
    serial = {}
    for k, v in state.items():
        serial[k] = v.tolist()
    return json.dumps(serial, sort_keys=True).encode("utf-8")

def prg_bytes_to_state(prg_bytes: bytes, shapes: List[Tuple[str, Tuple[int, ...]]]) -> Dict[str, np.ndarray]:
    """
    Convert PRG byte stream -> dict of numpy arrays with given shapes.
    Mapping: interpret bytes as uint32 little-endian chunks -> map to float32 in small range.
    """
    # Convert bytes to uint32 stream
    # Ensure we have enough bytes: each float32 needs 4 bytes
    floats_needed = sum(int(np.prod(s)) for (_, s) in shapes)
    required_bytes = floats_needed * 4
    if len(prg_bytes) < required_bytes:
        # stretch deterministically via repeated hashing (the caller should ensure enough length)
        prg_bytes = (prg_bytes * (math.ceil(required_bytes / len(prg_bytes)) + 1))[:required_bytes]
    arr = np.frombuffer(prg_bytes[:required_bytes], dtype=np.uint32).astype(np.uint32)
    # map uint32 -> float32 small range [-1e-3, 1e-3]
    # we divide by 2^32 and shift to [-0.5,0.5]*scale
    floats = (arr.astype(np.float64) / float(2**32) - 0.5) * 2e-3
    floats = floats.astype(np.float32)
    out = {}
    idx = 0
    for k, shape in shapes:
        size = int(np.prod(shape))
        seg = floats[idx: idx + size]
        out[k] = seg.reshape(shape).astype(np.float32)
        idx += size
    return out

def add_state_dicts(a: Dict[str, np.ndarray], b: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    out = {}
    for k in a:
        out[k] = (a[k].astype(np.float32) + b.get(k, 0.0)).astype(np.float32)
    return out

def sub_state_dicts(a: Dict[str, np.ndarray], b: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    out = {}
    for k in a:
        out[k] = (a[k].astype(np.float32) - b.get(k, 0.0)).astype(np.float32)
    return out
