"""
IPFSClient wrapper.

- Primary: uses ipfshttpclient (connects to local go-ipfs / remote provider)
- Fallback: LocalContentAddressedStore (uses sha256 and local files)
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
import tempfile

try:
    import ipfshttpclient
    HAS_IPFS = True
except Exception:
    HAS_IPFS = False

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

class LocalContentAddressedStore:
    def __init__(self, storage_dir: str = "./ipfs_fallback_store"):
        self.dir = storage_dir
        os.makedirs(self.dir, exist_ok=True)

    def add_bytes(self, b: bytes) -> str:
        cid = _sha256_bytes(b)
        path = os.path.join(self.dir, cid + ".bin")
        with open(path, "wb") as f:
            f.write(b)
        return cid

    def get_bytes(self, cid: str) -> Optional[bytes]:
        path = os.path.join(self.dir, cid + ".bin")
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def add_state(self, state: Dict[str, Any]) -> str:
        b = json.dumps(_serialize_state(state)).encode("utf-8")
        return self.add_bytes(b)

    def get_state(self, cid: str) -> Optional[Dict[str, Any]]:
        b = self.get_bytes(cid)
        if b is None:
            return None
        return json.loads(b.decode("utf-8"))

def _serialize_state(s):
    # convert numpy arrays to lists if present
    try:
        import numpy as _np
    except Exception:
        _np = None
    if isinstance(s, dict):
        out = {}
        for k, v in s.items():
            if _np is not None and isinstance(v, _np.ndarray):
                out[k] = v.tolist()
            elif isinstance(v, dict):
                out[k] = _serialize_state(v)
            else:
                out[k] = v
        return out
    return s

class IPFSClient:
    def __init__(self, api_multiaddr: str = "/ip4/127.0.0.1/tcp/5001", storage_dir: str = "./ipfs_fallback_store"):
        self._use_ipfs = HAS_IPFS
        self._storage_dir = storage_dir
        if self._use_ipfs:
            try:
                self._client = ipfshttpclient.connect(api_multiaddr)
            except Exception:
                self._client = None
                self._use_ipfs = False
        if not self._use_ipfs:
            self._store = LocalContentAddressedStore(storage_dir)

    def add_state(self, state: Dict[str, Any]) -> str:
        if self._use_ipfs and self._client is not None:
            # ipfshttpclient expects bytes or file-like
            temp = json.dumps(_serialize_state(state)).encode("utf-8")
            res = self._client.add_bytes(temp)
            # res is a hash-like string; we return it as cid
            return res
        else:
            return self._store.add_state(state)

    def get_state(self, cid: str) -> Optional[Dict[str, Any]]:
        if self._use_ipfs and self._client is not None:
            try:
                b = self._client.cat(cid)
                if isinstance(b, bytes):
                    return json.loads(b.decode("utf-8"))
                else:
                    return json.loads(b)
            except Exception:
                return None
        else:
            return self._store.get_state(cid)

    def add_bytes(self, b: bytes) -> str:
        if self._use_ipfs and self._client is not None:
            return self._client.add_bytes(b)
        else:
            return self._store.add_bytes(b)

    def get_bytes(self, cid: str) -> Optional[bytes]:
        if self._use_ipfs and self._client is not None:
            try:
                return self._client.cat(cid)
            except Exception:
                return None
        else:
            return self._store.get_bytes(cid)
