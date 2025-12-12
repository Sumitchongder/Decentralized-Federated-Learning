class WebRTCSignaler:
    """
    Simple WebRTC signaling manager
    """
    def __init__(self):
        self.clients = {}

    def register_client(self, client_id, offer=None):
        self.clients[client_id] = {"offer": offer, "answer": None}

    def set_answer(self, client_id, answer):
        if client_id in self.clients:
            self.clients[client_id]["answer"] = answer

    def get_peer_offer(self, client_id):
        return self.clients.get(client_id, {}).get("offer", None)

    def get_peer_answer(self, client_id):
        return self.clients.get(client_id, {}).get("answer", None)
