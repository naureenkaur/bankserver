import socket
import os
import random
import json
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Define global variables
AUDIT_LOG_FILE = "audit_log.txt"
BALANCES_FILE = "user_balances.json"

# Load initial user balances from JSON file
def load_user_balances():
    try:
        with open(BALANCES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {BALANCES_FILE} not found.")
        return {}

# Save user balances to JSON file
def save_user_balances(user_balances):
    with open(BALANCES_FILE, "w") as file:
        json.dump(user_balances, file)

# Dictionary to store account information (username, password, balance)
user_balances = load_user_balances()

def log_transaction(username, action, amount):
    """
    Log the transaction information into an audit log file.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG_FILE, "a") as file:
        file.write(f"Username: {username}, Action: {action}, Amount: {amount}, Time: {now} \n")

def add_funds(username, amount):
    """
    Add funds to a user's account.
    """
    if username in user_balances:
        user_balances[username] += amount
        save_user_balances(user_balances)
        log_transaction(username, "Add Funds", amount)
        return True
    else:
        print(f"Error: User '{username}' not found.")
        return False

def remove_funds(username, amount):
    """
    Remove funds from a user's account.
    """
    if username in user_balances:
        if user_balances[username] >= amount:
            user_balances[username] -= amount
            save_user_balances(user_balances)
            log_transaction(username, "Remove Funds", amount)
            return True
        else:
            print(f"Error: Insufficient funds in user '{username}' account.")
            return False
    else:
        print(f"Error: User '{username}' not found.")
        return False

def view_transaction_history():
    """
    View the transaction history from the audit log file.
    """
    try:
        with open(AUDIT_LOG_FILE, "r") as file:
            print("Transaction History:")
            print(file.read())
    except FileNotFoundError:
        print("Error: Audit log file not found.")

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
    CLIENT_3_ID = "HostKDC"
    KEY_STRING_1 = "key1"
    KEY_STRING_2 = "key2"
    KEY_STRING_3 = "key3"

    # Generate RSA key pair for server
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # AES key generator
    key_gen_aes = rsa.generate_private_key(
        public_exponent=65537,
        key_size=128,
        backend=default_backend()
    )

    # Open the server and initialize it as 3007
    port_number = 3007
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', port_number))
        server_socket.listen()
        print("Server started and listening for connections...")

        # Connect to client 1
        client1_socket, client1_address = server_socket.accept()
        print("Client 1 connected:", client1_address)

        with client1_socket.makefile('wb', buffering=0) as d_out1, client1_socket.makefile('rb', buffering=0) as d_in1:
            # Read client 1's public key
            client1_public_key_length = int.from_bytes(d_in1.read(4), byteorder='big')
            client1_public_key_bytes = d_in1.read(client1_public_key_length)
            client1_public_key = serialization.load_pem_public_key(
                client1_public_key_bytes,
                backend=default_backend()
            )
            print("Client 1's public key:", client1_public_key)

            # Read client 1's ID
            client1_id = d_in1.readline().decode().strip()
            print("Client 1's ID:", client1_id)

            # Generate nonce and ID pair
            random_array1 = [random.randint(0, 1) for _ in range(16)]
            nonce1 = ''.join(map(str, random_array1))
            nonce_id_pair1 = nonce1 + "-" + CLIENT_3_ID

            # Encrypt nonce and ID pair with client 1's public key
            cipher_nonce_id_pair1 = encrypt_data_rsa(nonce_id_pair1.encode(), client1_public_key)

            # Send cipher to client 1
            d_out1.write(len(cipher_nonce_id_pair1).to_bytes(4, byteorder='big'))
            d_out1.write(cipher_nonce_id_pair1)
