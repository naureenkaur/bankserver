import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import secrets
from key_derivation import derive_keys  # Make sure to implement derive_keys properly

# Master Secret key should be securely managed and stored
MASTER_SECRET = b'YourMasterSecretHere'  # Replace with your actual securely managed master secret

# Derive AES and MAC keys from the master secret
AES_KEY, MAC_KEY = derive_keys(MASTER_SECRET)

def generate_mac(data):
    """
    Generate a Message Authentication Code (MAC) for data integrity.
    """
    return hmac.new(MAC_KEY, data, hashlib.sha256).digest()

def verify_mac(data, mac_received):
    """
    Verify the Message Authentication Code (MAC) for data integrity.
    """
    return hmac.compare_digest(generate_mac(data), mac_received)

def encrypt(message):
    """
    Encrypts a message using AES encryption in CBC mode with PKCS7 padding.
    """
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_message = padder.update(message.encode('utf-8')) + padder.finalize()

    iv = secrets.token_bytes(16)  # Generate a random IV
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(padded_message) + encryptor.finalize()

    return iv + cipher_text

def decrypt(cipher_text):
    """
    Decrypts a message using AES decryption in CBC mode with PKCS7 padding.
    """
    iv = cipher_text[:16]
    cipher_text = cipher_text[16:]

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(cipher_text) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_message = unpadder.update(padded_message) + unpadder.finalize()

    return decrypted_message.decode('utf-8')
