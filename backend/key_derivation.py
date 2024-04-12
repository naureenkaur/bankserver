from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

def derive_encryption_and_mac_keys(master_secret, salt=None, info=b'handshake data encryption and mac'):
    """
    Derive two keys from the master secret using HKDF: one for encryption, one for MAC.
    
    Parameters:
        master_secret (bytes): The shared master secret.
        salt (bytes): Optional salt value (a non-secret random value); if not provided, it's assumed to be all zeros.
        info (bytes): Optional context and application specific information.
    
    Returns:
        tuple: Contains two bytes objects, the first for encryption key and the second for MAC key.
    """
    # HKDF setup to derive keys
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,  # Total bytes: 32 for AES key, 32 for MAC key
        salt=salt,
        info=info,
        backend=default_backend()
    )
    
    # Derive keys
    derived_keys = hkdf.derive(master_secret)
    
    # Split the derived bytes into an encryption key and a MAC key
    encryption_key = derived_keys[:32]
    mac_key = derived_keys[32:]
    
    return encryption_key, mac_key
