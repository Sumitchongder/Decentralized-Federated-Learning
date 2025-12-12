import torch
import json
import os

def save_state(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(obj, dict):
        torch.save(obj, path)
    else:
        torch.save(obj.state_dict(), path)

def load_state(model, path):
    if os.path.exists(path):
        state = torch.load(path)
        if isinstance(state, dict):
            model.load_state_dict(state)
        else:
            model.load_state_dict(state)
        return model
    raise FileNotFoundError(f"File {path} not found")
