class PinManager:
    """
    Stub for IPFS pinning service
    """
    def __init__(self):
        self.pinned_cids = set()

    def pin(self, cid: str):
        self.pinned_cids.add(cid)

    def unpin(self, cid: str):
        self.pinned_cids.discard(cid)

    def is_pinned(self, cid: str):
        return cid in self.pinned_cids
