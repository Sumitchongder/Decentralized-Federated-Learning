"""
IPFS client wrapper for PolyScale-FL.

Provides:
- IPFSClient: attempts to use a running IPFS HTTP API (ipfshttpclient).
- LocalIPFSFallback: content-addressed local store used when IPFS daemon is not available.

API:
    ipfs = IPFSClient()
    cid = ipfs.add_state(state_dict)
    data = ipfs.get(cid)
"""
__all__ = ["ipfs_client"]
