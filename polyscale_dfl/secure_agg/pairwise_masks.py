import torch

def generate_pairwise_masks(update: dict, peers: list):
    """
    Generate pairwise random masks between clients for secure aggregation.
    Returns masked update and mask dictionary.
    """
    masks = {peer: {k: torch.randn_like(v) for k, v in update.items()} for peer in peers}
    masked_update = {k: v.clone() for k, v in update.items()}
    for peer_masks in masks.values():
        for k in masked_update:
            masked_update[k] += peer_masks[k]
    return masked_update, masks
