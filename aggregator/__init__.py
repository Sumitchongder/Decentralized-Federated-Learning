"""
polyscale_fl.aggregator
=======================

Aggregator package for PolyScale-FL.

Modules:
- aggregator_node: AggregatorNode class — receives updates, coordinates secure aggregation,
                   applies FedAvg/FedProx, snapshots models to IPFS, publishes to chain.
- scheduler: round scheduler supporting synchronous and asynchronous collection policies.
- evaluator: evaluation utilities to test global model on sampled client data.
- orchestration: CLI / bootstrap helper to run an aggregator process (for local playground / docker).
"""
__all__ = ["aggregator_node", "scheduler", "evaluator", "orchestration"]
