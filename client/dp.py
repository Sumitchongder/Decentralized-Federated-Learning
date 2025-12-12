"""
Differential Privacy utilities

- gaussian_noise: adds Gaussian noise to numpy-based parameter dicts
- clip_gradients: l2-clips a parameter dict (useful before DP noise)
- dp_aggregate: aggregator-side noise addition (if using central DP)
"""

from typing import Dict
import numpy as np

def clip_update_l2(update: Dict[str, np.ndarray], max_norm: float) -> Dict[str, np.ndarray]:
    """Clip the whole update to have l2 norm <= max_norm"""
    total_sq = 0.0
    for v in update.values():
        total_sq += float((v ** 2).sum())
    total_norm = np.sqrt(total_sq)
    if total_norm <= max_norm:
        return update
    scale = max_norm / (total_norm + 1e-12)
    return {k: (v * scale).astype(np.float32) for k, v in update.items()}

def gaussian_noise_like(update: Dict[str, np.ndarray], sigma: float, rng: np.random.RandomState = None) -> Dict[str, np.ndarray]:
    """Return a new dict with Gaussian noise (sigma is stddev) added to each array."""
    rng = rng or np.random.RandomState()
    noisy = {}
    for k, v in update.items():
        noise = rng.normal(loc=0.0, scale=sigma, size=v.shape).astype(np.float32)
        noisy[k] = (v + noise)
    return noisy

def apply_dp_to_update(update: Dict[str, np.ndarray], max_norm: float, sigma: float, rng: np.random.RandomState = None):
    """Clip then add Gaussian noise to implement the Gaussian mechanism per-update."""
    clipped = clip_update_l2(update, max_norm)
    return gaussian_noise_like(clipped, sigma, rng=rng)
