import torch

def apply_dp(update: dict, noise_std: float):
    """Apply Gaussian noise to model updates for differential privacy"""
    dp_update = {}
    for k, v in update.items():
        dp_update[k] = v + torch.randn_like(v) * noise_std
    return dp_update
