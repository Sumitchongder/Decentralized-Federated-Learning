class FLContractStub:
    """
    Simple stub for FL blockchain contract interactions.
    Simulates committing updates and retrieving history.
    """
    def __init__(self):
        self.update_history = []

    def commit_update(self, cid: str):
        tx_hash = f"tx_{len(self.update_history)+1}"
        self.update_history.append({"cid": cid, "tx_hash": tx_hash})
        return tx_hash

    def get_update_history(self):
        return [u["cid"] for u in self.update_history]
