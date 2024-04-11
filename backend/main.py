from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import hashlib
import os
import json
from cryptography.exceptions import InvalidSignature
from database import authenticate_user, add_funds, remove_funds
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app)
CORS(app, origins=["http://localhost:3000"])

# Store keys securely or use a secure key management service
MASTER_SECRET = b'COE817'  # Replace with your actual master secret

# Derive keys from the master secret
def derive_keys():
    # For HKDF, you need to use the same salt on both client and server
    salt = b'predefined-salt-that-is-secure-and-static'  # Replace with your actual salt
    backend = default_backend()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b'handshake data',
        backend=backend
    )
    derived_key = hkdf.derive(MASTER_SECRET)
    encryption_key = derived_key[:16]
    mac_key = derived_key[16:]
    return encryption_key, mac_key

# Decrypt data using AES-CFB
def decrypt_data(encryption_key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# Verify MAC for data integrity
def verify_mac(mac_key, data, mac):
    h = hmac.HMAC(mac_key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    try:
        h.verify(mac)
        return True
    except InvalidSignature:
        return False

# Decrypt data using AES-GCM
def decrypt_aes_gcm(key, encrypted_data):
    aesgcm = AESGCM(key)
    encrypted_data = base64.b64decode(encrypted_data)
    nonce = encrypted_data[:12]
    ct = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ct, None).decode('utf-8')

# Generate MAC for data integrity
def generate_mac(key, data):
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    return h.finalize()

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if authenticate_user(username, password):
        # This is a simplified example. In a real application, you should return a secure token (e.g., JWT)
        return jsonify({"message": "Login successful", "authenticated": True}), 200
    else:
        return jsonify({"message": "Login failed", "authenticated": False}), 401

# Add Money Endpoint
@app.route('/add_money', methods=['POST'])
def add_money():
    # This assumes the client sends the IV, ciphertext, and MAC separately
    encrypted_data = request.json.get('encryptedData')
    mac = request.json.get('mac')
    # Convert from base64 to bytes
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    iv = encrypted_data_bytes[:16]  # The first 16 bytes should be the IV
    ciphertext = encrypted_data_bytes[16:]  # The rest is ciphertext

    encryption_key, mac_key = derive_keys()
    if verify_mac(mac_key, ciphertext, base64.b64decode(mac)):
        decrypted_data = decrypt_data(encryption_key, iv, ciphertext)
        data = json.loads(decrypted_data)
        username = data.get('username')
        amount = data.get('amount')
        add_funds(username, amount)
        return jsonify({"message": f"Added {amount} to {username}'s account"}), 200
    else:
        return jsonify({"message": "MAC verification failed"}), 403

# Withdraw Money Endpoint
@app.route('/withdraw_money', methods=['POST'])
def withdraw_money():
    username = request.json.get('username')
    amount = request.json.get('amount')
    remove_funds(username, amount)
    return jsonify({"message": f"Withdrew {amount} from {username}'s account"}), 200

# View Balance Endpoint
@app.route('/view_balance', methods=['POST'])
def view_balance():
    username = request.json.get('username')
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''SELECT amount FROM users WHERE username = ?''', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({"balance": result[0]}), 200
    else:
        return jsonify({"message": "User not found"}), 404

# Download Audit Log Endpoint
@app.route('/download_audit_log', methods=['GET'])
def download_audit_log():
    filepath = os.path.join(os.getcwd(), "transaction_log.txt")
    try:
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        return "File not found.", 404

# Logout Endpoint (Example Placeholder)
@app.route('/logout', methods=['GET'])
def logout():
    # Implement session or token invalidation logic here
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
