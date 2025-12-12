from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import torch

def generate_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt_tensor(tensor: torch.Tensor, public_key):
    """
    Encrypt tensor by flattening and encrypting each element (toy example)
    """
    flattened = tensor.flatten().tolist()
    encrypted = [public_key.encrypt(
        int(x).to_bytes(4, 'big'), 
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    ) for x in flattened]
    return encrypted

def decrypt_tensor(encrypted_list, private_key, shape):
    decrypted = [int.from_bytes(private_key.decrypt(
        e,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    ), 'big') for e in encrypted_list]
    return torch.tensor(decrypted).reshape(shape)
