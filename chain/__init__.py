"""
Blockchain interaction layer for PolyScale-FL.

Contains:
- chain_stub: Minimal offline ledger emulation used for playgrounds and local demos.
- web3_client: Production Web3 implementation communicating with deployed contracts.
- Solidity contracts defining:
    * ModelRegistry — Stores model CIDs and metadata.
    * RewardToken — ERC20 reward token for FL participation.
    * Reputation   — Tracks node reputation scores.
"""
__all__ = ["chain_stub", "web3_client"]
