import os
import torch

class CheckpointManager:
    """
    Save and load model checkpoints for FL
    """
    def __init__(self, checkpoint_dir="./checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def save(self, model, round_number):
        path = os.path.join(self.checkpoint_dir, f"round_{round_number}.pt")
        torch.save(model.state_dict(), path)
        print(f"[Checkpoint] Saved model for round {round_number} at {path}")

    def load(self, model, round_number):
        path = os.path.join(self.checkpoint_dir, f"round_{round_number}.pt")
        if os.path.exists(path):
            model.load_state_dict(torch.load(path))
            print(f"[Checkpoint] Loaded model from round {round_number}")
        else:
            print(f"[Checkpoint] No checkpoint found for round {round_number}")
