"""
polyscale_fl.client
===================

Client-side package for PolyScale-FL:
- trainer: local training loop (PyTorch and NumPy fallbacks)
- client_node: orchestration for federated participation
- datasets: connectors for common datasets (Torchvision / HF / synthetic)
- dp: differential privacy utilities
- mpc: secure-aggregation / mask management stubs (Bonawitz integration points)
- cli: small entrypoint for running a client in a container
"""

__all__ = [
    "trainer",
    "client_node",
    "datasets",
    "dp",
    "mpc",
    "cli"
]
