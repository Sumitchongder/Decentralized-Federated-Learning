import torch

def generate_pairwise_masks(update: dict, peers: list):
    """
    Generate pairwise additive masks for Bonawitz-style secure aggregation.
    Each peer shares a mask secretly to cancel out during aggregation.
    """
    masks = {peer: {k: torch.randn_like(v) for k, v in update.items()} for peer in peers}
    masked_update = update.copy()
    for peer_masks in masks.values():
        for k in masked_update:
            masked_update[k] += peer_masks[k]
    return masked_update, masks
