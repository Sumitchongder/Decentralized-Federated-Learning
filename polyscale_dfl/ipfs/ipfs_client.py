import json
import os

class IPFSClient:
    """
    Simplified IPFS client stub.
    Replace with real IPFS HTTP client for production.
    """
    def __init__(self, storage_dir="./ipfs_storage"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def upload_json(self, data: dict):
        """
        Simulate uploading JSON to IPFS and return a fake CID.
        """
        cid = f"Qm{len(os.listdir(self.storage_dir)) + 1:06d}"
        with open(os.path.join(self.storage_dir, cid + ".json"), "w") as f:
            json.dump(data, f)
        return cid

    def fetch_json(self, cid: str):
        path = os.path.join(self.storage_dir, cid + ".json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        raise FileNotFoundError(f"CID {cid} not found in local storage")
