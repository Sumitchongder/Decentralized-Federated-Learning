"""
Web3 Contract Interface for PolyScale-FL
----------------------------------------

Handles interactions with:
- ModelRegistry
- RewardToken
- Reputation

Requirements:
    pip install web3

Configure:
    export WEB3_RPC=http://localhost:8545
    export POLYSCALE_REGISTRY=0x...
    export POLYSCALE_TOKEN=0x...
    export POLYSCALE_REPUTATION=0x...
"""

import os
import json
from typing import Dict, Any
from web3 import Web3

class PolyScaleWeb3:
    def __init__(
        self,
        rpc_url: str = None,
        registry_address: str = None,
        token_address: str = None,
        reputation_address: str = None,
    ):
        rpc_url = rpc_url or os.getenv("WEB3_RPC", "http://127.0.0.1:8545")
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        root = os.path.join(os.path.dirname(__file__), "contracts", "hardhat", "artifacts")

        def load_abi(contract_name):
            path = os.path.join(root, "contracts", f"{contract_name}.sol", f"{contract_name}.json")
            with open(path) as f:
                return json.load(f)["abi"]

        # Contract addresses (env variables recommended)
        self.registry_address = registry_address or os.getenv("POLYSCALE_REGISTRY")
        self.token_address = token_address or os.getenv("POLYSCALE_TOKEN")
        self.rep_address = reputation_address or os.getenv("POLYSCALE_REPUTATION")

        self.registry = self.web3.eth.contract(
            address=self.registry_address,
            abi=load_abi("ModelRegistry")
        )

        self.token = self.web3.eth.contract(
            address=self.token_address,
            abi=load_abi("RewardToken")
        )

        self.reputation = self.web3.eth.contract(
            address=self.rep_address,
            abi=load_abi("Reputation")
        )

    # ---------------- Smart Contract Calls ---------------- #

    def register_model(self, cid: str, round_number: int, metrics: Dict[str, float], sender):
        tx = self.registry.functions.registerModel(
            cid,
            round_number,
            json.dumps(metrics)
        ).transact({"from": sender})
        return tx

    def reward(self, node: str, amount: int, sender):
        tx = self.token.functions.reward(node, amount).transact({"from": sender})
        return tx

    def set_reputation(self, node: str, score: int, sender):
        tx = self.reputation.functions.setReputation(node, score).transact({"from": sender})
        return tx

    def get_balance(self, node: str):
        return self.token.functions.balanceOf(node).call()
