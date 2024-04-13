import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend  # Correct import for default_backend

def derive_keys(master_secret):
    """
    Derives AES and MAC keys from the master secret using HKDF.
    Args:
    - master_secret (bytes): The master secret.
    Returns:
    - encryption_key (bytes): Key for data encryption.
    - mac_key (bytes): Key for message authentication code.
    """
    # Use a random salt, securely generated for key derivation
    salt = os.urandom(16)  # A secure random salt
    info_encryption = b'encryption_key'
    info_mac = b'mac_key'

    # HKDF instance for deriving an encryption key
    hkdf_encryption = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info_encryption,
        backend=default_backend()
    )
    
    # HKDF instance for deriving a MAC key
    hkdf_mac = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info_mac,
        backend=default_backend()
    )

    encryption_key = hkdf_encryption.derive(master_secret)
    mac_key = hkdf_mac.derive(master_secret)

    return encryption_key, mac_key

# Example usage
if __name__ == "__main__":
    master_secret = b'YourMasterSecretHere'  # Replace with your actual securely managed master secret
    encryption_key, mac_key = derive_keys(master_secret)
    print("Encryption Key:", encryption_key.hex())
    print("MAC Key:", mac_key.hex())
