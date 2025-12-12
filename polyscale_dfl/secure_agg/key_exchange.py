from .crypto_utils import generate_keypair

class KeyExchange:
    """
    Simulated Diffie-Hellman / RSA key exchange between clients
    """
    def __init__(self):
        self.keys = {}

    def register_client(self, client_id):
        private_key, public_key = generate_keypair()
        self.keys[client_id] = {"private": private_key, "public": public_key}
        return public_key

    def get_public_key(self, client_id):
        return self.keys[client_id]["public"]

    def get_private_key(self, client_id):
        return self.keys[client_id]["private"]
