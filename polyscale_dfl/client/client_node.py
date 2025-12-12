import torch
from .trainer import train_one_round
from .dp import apply_dp
from .mpc_masking import generate_pairwise_masks

class ClientNode:
    def __init__(self, id: int, model, train_loader, dp_noise=0.0):
        self.id = id
        self.model = model
        self.train_loader = train_loader
        self.dp_noise = dp_noise
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def train_one_round(self, epochs=1):
        """Train locally and return weight update"""
        update = train_one_round(self.model, self.train_loader, epochs, self.device)
        if self.dp_noise > 0.0:
            update = apply_dp(update, self.dp_noise)
        return update

    def mask_update(self, peers):
        """Generate pairwise masks with other clients for secure aggregation"""
        masked_update, masks = generate_pairwise_masks(self.model.state_dict(), peers)
        return masked_update, masks
