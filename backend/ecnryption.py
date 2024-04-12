import hashlib
import hmac
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

def generate_keys():
    """Generate ECDH private and public key pair."""
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
    return private_key, private_key.public_key()

def serialize_public_key(public_key):
    """Serialize the public key to a PEM format."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_public_key(pem):
    """Deserialize the PEM formatted public key."""
    return serialization.load_pem_public_key(pem, backend=default_backend())

def derive_keys(shared_secret):
    """Derive symmetric encryption and MAC keys from a shared secret."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,  # 32 bytes for encryption, 32 bytes for MAC
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    )
    key = hkdf.derive(shared_secret)
    return key[:32], key[32:]

def encrypt(data, key):
    """Encrypt data using AES."""
    cipher = Cipher(algorithms.AES(key), modes.CFB(os.urandom(16)), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    iv = encryptor._ctx._backend._lib.Cryptography_cipher_ctx_get_iv(encryptor._ctx._ctx)
    return iv + encryptor.update(padded_data) + encryptor.finalize()

def decrypt(encrypted_data, key):
    """Decrypt data using AES."""
    iv = encrypted_data[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    padded_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
    return unpadder.update(padded_data) + unpadder.finalize()

def create_hmac(data, key):
    """Create HMAC for data integrity."""
    h = hmac.new(key, data, hashlib.sha256)
    return h.digest()

def verify_hmac(data, key, tag):
    """Verify HMAC."""
    h = hmac.new(key, data, hashlib.sha256)
    return hmac.compare_digest(h.digest(), tag)
