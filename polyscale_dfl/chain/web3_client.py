from web3 import Web3

class Web3Client:
    """
    Web3 client to interact with Ethereum-compatible blockchain.
    """
    def __init__(self, rpc_url="http://127.0.0.1:8545"):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.web3.is_connected(), "Cannot connect to blockchain node"

    def get_balance(self, address: str):
        return self.web3.eth.get_balance(address)

    def send_transaction(self, tx):
        tx_hash = self.web3.eth.send_transaction(tx)
        return tx_hash.hex()
