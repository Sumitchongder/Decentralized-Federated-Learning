"""
Evaluator utilities.

Purpose:
- Evaluate a global model state on sample data provided by clients (or held-out dataset)
- Provide a simple interface used by aggregator orchestration/monitoring

Notes:
- Works on numpy-state dict models created by trainer.Trainer.get_state
- For PyTorch models, orchestration can create a fresh Trainer and call Trainer.set_state before evaluation
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
try:
    import torch
    USE_TORCH = True
except Exception:
    USE_TORCH = False

def eval_state_on_sample(state: Dict[str, np.ndarray], samples: List[Tuple[np.ndarray, np.ndarray]], batch_size: int = 64) -> Tuple[float, float]:
    """
    Evaluate the provided state on combined samples.
    returns (loss, acc) — simple approximate loss/acc for numpy MLP architecture.
    """
    # reconstruct simple numpy model forward (must be compatible with trainer's simple MLP)
    Xs = []
    ys = []
    for X, y in samples:
        Xs.append(X)
        ys.append(y)
    X = np.vstack(Xs)
    y = np.concatenate(ys)
    # forward
    h = np.tanh(X.dot(state["W1"]) + state["b1"])
    logits = h.dot(state["W2"]) + state["b2"]
    preds = logits.argmax(axis=1)
    acc = (preds == y).mean()
    # crude loss: negative log likelihood surrogate
    probs = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)
    eps = 1e-12
    nll = -np.log(np.clip(probs[np.arange(len(y)), y], eps, 1.0)).mean()
    return float(nll), float(acc)
