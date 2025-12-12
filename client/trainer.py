"""
Trainer module for local training.

Features:
- supports PyTorch training loop (preferred)
- numpy fallback simple MLP training for environments without torch
- provides APIs to return model weights as numpy dicts and load weights from numpy dicts
- configurable callbacks to export intermediate metrics (used by client_node)
"""

from typing import Dict, Callable, Optional, Any
import numpy as np
import time
import math

USE_TORCH = False
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader
    USE_TORCH = True
except Exception:
    USE_TORCH = False

# Simple torch MLP
if USE_TORCH:
    class TorchMLP(nn.Module):
        def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )

        def forward(self, x):
            return self.net(x)

    def state_to_numpy(state: Dict[str, Any]) -> Dict[str, np.ndarray]:
        return {k: v.detach().cpu().numpy().astype(np.float32) for k, v in state.items()}

else:
    # Minimal numpy MLP used for fallback
    class NumpyMLP:
        def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, seed: Optional[int] = None):
            rng = np.random.RandomState(seed or 0)
            self.W1 = rng.normal(scale=0.1, size=(input_dim, hidden_dim)).astype(np.float32)
            self.b1 = np.zeros(hidden_dim, dtype=np.float32)
            self.W2 = rng.normal(scale=0.1, size=(hidden_dim, output_dim)).astype(np.float32)
            self.b2 = np.zeros(output_dim, dtype=np.float32)

        def forward(self, X: np.ndarray) -> np.ndarray:
            h = np.tanh(X.dot(self.W1) + self.b1)
            return h.dot(self.W2) + self.b2

        def get_weights(self) -> Dict[str, np.ndarray]:
            return {"W1": self.W1.copy(), "b1": self.b1.copy(), "W2": self.W2.copy(), "b2": self.b2.copy()}

        def set_weights(self, state: Dict[str, np.ndarray]):
            self.W1 = state["W1"].copy()
            self.b1 = state["b1"].copy()
            self.W2 = state["W2"].copy()
            self.b2 = state["b2"].copy()

def _to_numpy_state_torch(model) -> Dict[str, np.ndarray]:
    state = model.state_dict()
    return {k: v.detach().cpu().numpy().astype(np.float32) for k, v in state.items()}

def _from_numpy_state_torch(model, state_dict: Dict[str, np.ndarray]):
    import torch
    new_state = {k: torch.tensor(v) for k, v in state_dict.items()}
    model.load_state_dict(new_state)

class Trainer:
    """
    Trainer runs local training for a client. It abstracts framework differences and
    exposes:
      - trainer.train_one_epoch(...)
      - trainer.get_state() -> numpy dict
      - trainer.set_state(numpy_dict)
    """
    def __init__(self, model_cfg: Dict, device: Optional[str] = None, use_torch: Optional[bool] = None):
        self.model_cfg = model_cfg
        self.device = device or ("cuda" if USE_TORCH and torch.cuda.is_available() else "cpu")
        self.use_torch = USE_TORCH if use_torch is None else use_torch
        if self.use_torch:
            # lazy import torch modules
            self.model = TorchMLP(model_cfg["input_dim"], model_cfg["hidden_dim"], model_cfg["output_dim"])
            self.model.to(self.device)
            self.optim = optim.SGD(self.model.parameters(), lr=model_cfg.get("lr", 0.01), momentum=0.0)
            self.criterion = nn.CrossEntropyLoss()
        else:
            self.model = NumpyMLP(model_cfg["input_dim"], model_cfg["hidden_dim"], model_cfg["output_dim"], seed=model_cfg.get("seed", 0))

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 1, batch_size: int = 32, callbacks: Optional[Callable] = None):
        """
        Train locally. callbacks: optional function(metrics_dict) called after each epoch.
        """
        if self.use_torch:
            dataset = TensorDataset(torch.from_numpy(X), torch.from_numpy(y))
            loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            self.model.train()
            for e in range(epochs):
                epoch_loss = 0.0
                count = 0
                for xb, yb in loader:
                    xb = xb.to(self.device)
                    yb = yb.to(self.device)
                    self.optim.zero_grad()
                    logits = self.model(xb)
                    loss = self.criterion(logits, yb)
                    loss.backward()
                    self.optim.step()
                    epoch_loss += loss.item() * xb.size(0)
                    count += xb.size(0)
                metrics = {"epoch": e, "loss": epoch_loss / (count + 1e-12)}
                if callbacks:
                    callbacks(metrics)
            return metrics
        else:
            # very small SGD loop per sample for reproducibility in CPU-only environments
            n = X.shape[0]
            lr = self.model_cfg.get("lr", 0.01)
            for e in range(epochs):
                idx = np.random.permutation(n)
                total_loss = 0.0
                for i in idx:
                    xi = X[i:i+1]
                    yi = int(y[i])
                    h = np.tanh(xi.dot(self.model.W1) + self.model.b1)
                    logits = h.dot(self.model.W2) + self.model.b2
                    # softmax + cross-entropy gradient (two-class safe)
                    probs = np.exp(logits) / np.sum(np.exp(logits))
                    grad_out = probs
                    grad_out[0, yi] -= 1.0
                    grad_W2 = h.T.dot(grad_out)
                    grad_b2 = grad_out.flatten()
                    grad_h = grad_out.dot(self.model.W2.T) * (1 - h**2)
                    grad_W1 = xi.T.dot(grad_h)
                    grad_b1 = grad_h.flatten()
                    self.model.W2 -= lr * grad_W2
                    self.model.b2 -= lr * grad_b2
                    self.model.W1 -= lr * grad_W1
                    self.model.b1 -= lr * grad_b1
                    total_loss += -np.log(max(1e-12, probs[0, yi]))
                metrics = {"epoch": e, "loss": total_loss / n}
                if callbacks:
                    callbacks(metrics)
            return metrics

    def get_state(self) -> Dict[str, np.ndarray]:
        if self.use_torch:
            return _to_numpy_state_torch(self.model)
        else:
            return self.model.get_weights()

    def set_state(self, state: Dict[str, np.ndarray]):
        if self.use_torch:
            _from_numpy_state_torch(self.model, state)
        else:
            self.model.set_weights(state)
