"""
Aggregator orchestration CLI for running aggregator in a container / local machine.

- Parses env variables / args
- Boots P2P stub or integrates libp2p node (if configured)
- Boots IPFS client (real or fallback)
- Boots chain client (web3 wrapper or stub)
- Launches scheduler to run rounds
- Exposes a simple HTTP monitoring endpoint (optional)
"""

import os
import argparse
import logging
import time
from .aggregator_node import AggregatorNode
from .scheduler import Scheduler
from ..networking.p2p_stub import P2PStub
from ..ipfs.ipfs_client import IPFSClient
from ..chain.chain_stub import ChainStub

log = logging.getLogger("polyscale_fl.aggregator.orchestration")
logging.basicConfig(level=logging.INFO)

def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregator-id", default=os.environ.get("AGGREGATOR_ID", "aggregator_0"))
    parser.add_argument("--rounds", type=int, default=int(os.environ.get("ROUNDS", "10")))
    parser.add_argument("--clients", type=str, default=os.environ.get("CLIENT_LIST", "client_0,client_1,client_2"))
    parser.add_argument("--round-timeout", type=float, default=float(os.environ.get("ROUND_TIMEOUT", "6.0")))
    parser.add_argument("--clients-per-round", type=int, default=int(os.environ.get("CLIENTS_PER_ROUND", "2")))
    parser.add_argument("--secure-agg", action="store_true", default=bool(os.environ.get("SECURE_AGG", False)))
    return parser.parse_args()

def main():
    args = build_args()
    client_list = [c.strip() for c in args.clients.split(",") if c.strip()]

    # instantiate dependencies (stubs / wrappers)
    p2p = P2PStub()
    ipfs = IPFSClient()
    chain = ChainStub()

    # create aggregator
    agg = AggregatorNode(aggregator_id=args.aggregator_id, p2p_client=p2p, chain_client=chain, ipfs_client=ipfs)

    # register clients in p2p stub so they can be messaged (for local playground)
    for c in client_list:
        # clients should register their callbacks when started; in a single-process test we can set placeholders
        def _placeholder(from_id, payload):
            log.debug("placeholder received at %s from %s payload=%s", c, from_id, payload)
        p2p.register(c, _placeholder)

    scheduler = Scheduler(agg, p2p, client_list, round_timeout=args.round_timeout, clients_per_round=args.clients_per_round)
    scheduler.start_rounds(rounds=args.rounds, secure_agg=args.secure_agg)

    # keep alive while scheduler runs
    try:
        while scheduler._running:
            time.sleep(1.0)
    except KeyboardInterrupt:
        log.info("Shutting down aggregator orchestration")
        scheduler.stop()

if __name__ == "__main__":
    main()
