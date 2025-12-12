"""
Dataset connectors for Polyscale-FL clients.

This module exposes:
- get_synthetic_client_data: simple synthetic sample generator (for quick demos)
- CIFAR10 / MNIST connectors (torchvision) if torch is available
- HuggingFace connectors (optional)
Design notes:
- Each connector returns a dict with keys: X_train, y_train, X_val, y_val (numpy arrays)
- For large datasets use disk-backed dataloaders handled by trainer.Trainer
"""

from typing import Dict, Tuple, List, Optional
import numpy as np
from sklearn.model_selection import train_test_split

USE_TORCH = False
try:
    import torch
    from torchvision import datasets, transforms
    USE_TORCH = True
except Exception:
    USE_TORCH = False

def get_synthetic_client_data(n_clients: int = 4,
                              samples_per_client: int = 400,
                              n_features: int = 20,
                              n_classes: int = 2,
                              hetero: bool = True,
                              seed: int = 42) -> Dict[str, dict]:
    """
    Returns a mapping client_id -> {X_train, y_train, X_val, y_val}
    Useful for local demos and unit tests.
    """
    rng = np.random.RandomState(seed)
    clients = {}
    for i in range(n_clients):
        mean_shift = rng.normal(scale=0.5, size=n_features) if hetero else np.zeros(n_features)
        X = rng.normal(size=(samples_per_client, n_features)).astype(np.float32) + mean_shift
        # linear separable labels with noise
        w = rng.normal(size=(n_features, n_classes)).astype(np.float32)
        logits = X.dot(w)
        y = logits.argmax(axis=1).astype(np.int64)
        # add noise flips if hetero
        if hetero:
            flip_frac = rng.uniform(0.0, 0.2)
            nflip = int(samples_per_client * flip_frac)
            flip_idx = rng.choice(samples_per_client, size=nflip, replace=False)
            y[flip_idx] = (y[flip_idx] + 1) % n_classes
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=seed+i)
        clients[f"client_{i}"] = {
            "X_train": X_train,
            "y_train": y_train,
            "X_val": X_val,
            "y_val": y_val
        }
    return clients

def cifar10_connector(root: str = "./data", download: bool = True, client_partition: int = 0, n_clients: int = 4):
    """
    Partition CIFAR10 into `n_clients` shards and return the shard for `client_partition`.
    Returns dict like above but using numpy arrays.
    Requires torchvision.
    """
    if not USE_TORCH:
        raise RuntimeError("Torch/torchvision not available.")
    transform = transforms.Compose([
        transforms.ToTensor()
    ])
    ds = datasets.CIFAR10(root=root, train=True, download=download, transform=transform)
    total = len(ds)
    shard_size = total // n_clients
    start = client_partition * shard_size
    end = start + shard_size if client_partition < n_clients - 1 else total
    X = []
    y = []
    for i in range(start, end):
        img, label = ds[i]
        X.append(img.numpy())
        y.append(label)
    X = np.stack(X).astype(np.float32)
    y = np.array(y, dtype=np.int64)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    return {"X_train": X_train, "y_train": y_train, "X_val": X_val, "y_val": y_val}
