class CacheManager:
    """
    Simple in-memory cache for IPFS content
    """
    def __init__(self):
        self.cache = {}

    def add(self, cid: str, data):
        self.cache[cid] = data

    def get(self, cid: str):
        return self.cache.get(cid, None)

    def exists(self, cid: str):
        return cid in self.cache
