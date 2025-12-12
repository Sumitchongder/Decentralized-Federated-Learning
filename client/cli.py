"""
Command-line entrypoint for running a Polyscale-FL client inside a container.

This small CLI:
- parses environment variables for configuration
- instantiates minimal network/chain/ipfs stubs when those services are not provided
- runs local training rounds and sends updates (for demo / playground)
"""

import os
import time
import json
import argparse
import logging
from .client_node import ClientNode
from .datasets import get_synthetic_client_data
from ..networking.p2p_stub import P2PStub  # lightweight stub; real libp2p module will be provided separately
from ..chain.chain_stub import ChainStub  # stub; real web3 wrapper provided in chain module
from ..ipfs.ipfs_client import IPFSClient

log = logging.getLogger("polyscale_fl.client.cli")
logging.basicConfig(level=logging.INFO)

def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", default=os.environ.get("CLIENT_ID", "client_0"))
    parser.add_argument("--rounds", type=int, default=int(os.environ.get("ROUNDS", "5")))
    parser.add_argument("--epochs", type=int, default=int(os.environ.get("EPOCHS", "1")))
    parser.add_argument("--dp-sigma", type=float, default=float(os.environ.get("DP_SIGMA", "0.0")))
    parser.add_argument("--use-mpc", action="store_true")
    return parser.parse_args()

def main():
    args = build_args()
    # simple local stubs for playground mode
    network = P2PStub()
    chain = ChainStub()
    ipfs = IPFSClient(storage_dir="./ipfs_client_store")
    # small synthetic dataset per client
    data_map = get_synthetic_client_data(n_clients=1, samples_per_client=400, n_features=20, hetero=False, seed=42)
    data = list(data_map.values())[0]
    model_cfg = {"input_dim": 20, "hidden_dim": 64, "output_dim": 2, "lr": 0.05}
    client = ClientNode(args.client_id, model_cfg, data, network, chain, ipfs_client=ipfs, dp_sigma=args.dp_sigma, use_mpc=args.use_mpc)
    log.info("Client created: %s", args.client_id)
    # simple loop: run rounds and exit
    for r in range(args.rounds):
        log.info("Starting local round %d", r+1)
        res = client.local_train_and_prepare_update(epochs=args.epochs, batch_size=32)
        log.info("Round %d metrics: %s", r+1, json.dumps(res.get("metrics", {})))
        time.sleep(1.0)
    # publish final model
    cid = client.publish_model_to_ipfs()
    log.info("Published model CID: %s", cid)

if __name__ == "__main__":
    main()
