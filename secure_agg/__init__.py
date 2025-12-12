"""
polyscale_fl.secure_agg
=======================

Simplified Bonawitz-style secure aggregation implementation for PolyScale-FL.

Exposes:
- BonawitzClient: client-side protocol helpers (keypair creation, mask generation, commitments)
- BonawitzAggregator: aggregator-side helpers (collect public keys, accept masked updates, unmask)

This implementation uses:
- X25519 for pairwise ECDH (cryptography.hazmat)
- HKDF-SHA256 to expand shared secrets into deterministic PRG bytes
- NumPy to reshape PRG bytes into masks that match parameter shapes

Warning:
- Simplified dropout handling: clients can send mask-shares to aggregator when requested.
- Replace the dropout recovery with Shamir Secret Sharing (SSS) in production or use a dedicated library.
"""
__all__ = ["bonawitz", "utils"]
