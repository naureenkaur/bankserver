import socket
import os
import random
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def encrypt_data_rsa(data, key):
    cipher = key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return cipher

def decrypt_data_rsa(data, key):
    cipher = key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return cipher

def encrypt_data_aes(data, key):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    return ct

def decrypt_data_aes(data, key):
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    pt = decryptor.update(data) + decryptor.finalize()
    return pt

def main():
    CLIENT_1_ID = "ClientA"
    CLIENT_2_ID = "ClientB"

    # Generate RSA key pair for ClientA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Connect to server
    host = 'localhost'
    port = 3007
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        with sock.makefile('wb', buffering=0) as d_out, sock.makefile('rb', buffering=0) as d_in:
            # Send public key A
            byte_pubkey = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            d_out.write(len(byte_pubkey).to_bytes(4, byteorder='big'))
            d_out.write(byte_pubkey)

            # Send ID
            d_out.write(CLIENT_1_ID.encode() + b'\n')

            # Receive the EncryptedA nonceK + IDK
            encrypted_message1_length = int.from_bytes(d_in.read(4), byteorder='big')
            encrypted_message1 = d_in.read(encrypted_message1_length)
            message1 = decrypt_data_rsa(encrypted_message1, private_key).decode().split("-")
            host_nonce, host_id = message1[0], message1[1]
            print("Host nonce generated by hostKDC:", host_nonce)
            print("Host's ID received:", host_id)
            print("")

            # Receive the Server Public Key
            host_public_key_length = int.from_bytes(d_in.read(4), byteorder='big')
            host_public_key_bytes = d_in.read(host_public_key_length)
            host_public_key = serialization.load_pem_public_key(
                host_public_key_bytes,
                backend=default_backend()
            )
            print("Host's public key:", host_public_key)
            print("")

            # Prepare the encryptedK nonceA + nonceK
            random_array1 = [random.randint(0, 1) for _ in range(16)]
            nonce1 = ''.join(map(str, random_array1))
            double_nonce = f"{nonce1}-{host_nonce}"
            print("Client 1's nonce + hostKDC's nonce:", double_nonce)
            print("")

            # Encrypt the nonce-ID pair with host's public key
            double_nonce_encrypted = encrypt_data_rsa(double_nonce.encode(), host_public_key)

            # Send the encrypted double nonce to host
            d_out.write(len(double_nonce_encrypted).to_bytes(4, byteorder='big'))
            d_out.write(double_nonce_encrypted)

            # Receive encryptedA host nonce
            host_nonce_check_length = int.from_bytes(d_in.read(4), byteorder='big')
            host_nonce_check_bytes = d_in.read(host_nonce_check_length)
            host_nonce_check = decrypt_data_rsa(host_nonce_check_bytes, private_key).decode().split("-")[0]
            print("Host nonce generated by hostKDC:", host_nonce_check)
            print("")

            # Receive double encrypted symmetric key
            # Receive + decrypt the front half
            encrypted_front_length = int.from_bytes(d_in.read(4), byteorder='big')
            encrypted_front_half = d_in.read(encrypted_front_length)
            decrypted_front_half = decrypt_data_rsa(encrypted_front_half, private_key)

            # Receive + decrypt the back half
            encrypted_back_length = int.from_bytes(d_in.read(4), byteorder='big')
            encrypted_back_half = d_in.read(encrypted_back_length)
            decrypted_back_half = decrypt_data_rsa(encrypted_back_half, private_key)

            # Concatenate the two halves of the key
            decrypted_sym_key = decrypted_front_half + decrypted_back_half

            # Final Decrypt
            symmetric_key = decrypt_data_rsa.decrypt(decrypted_sym_key, padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
            # Phase 2:
            # Send ClientIDA and ClientIDB
            d_out.write(f"{CLIENT_1_ID}-{CLIENT_2_ID}".encode() + b'\n')

            # Receive the Kab and decrypt
            encrypted_kab_length = int.from_bytes(d_in.read(4), byteorder='big')
            encrypted_kab = d_in.read(encrypted_kab_length)
            decrypted_kab = decrypt_data_aes(encrypted_kab, symmetric_key)

            session_key_kab = decrypted_kab
            print("Session key Kab:", session_key_kab)
            print("")

if __name__ == "__main__":
    main()