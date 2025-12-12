class P2PNode:
    """
    Simplified P2P node stub for testing.
    """
    def __init__(self, id):
        self.id = id
        self.peers = {}
        self.inbox = []

    def connect_peer(self, peer_node):
        self.peers[peer_node.id] = peer_node

    def send_message(self, peer_id, message):
        if peer_id in self.peers:
            self.peers[peer_id].inbox.append(message)

    def receive_message(self):
        if self.inbox:
            return self.inbox.pop(0)
        return None
