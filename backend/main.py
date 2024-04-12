from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import hashlib
import os
from database import authenticate_user, add_funds, remove_funds
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Generate server's private key for key exchange (ephemeral)
private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())

@app.route('/exchange_keys', methods=['POST'])
def exchange_keys():
    client_public_key_data = request.json['public_key']
    client_public_key = serialization.load_pem_public_key(
        base64.b64decode(client_public_key_data.encode()),
        backend=default_backend()
    )

    # Generate shared secret
    shared_secret = private_key.exchange(ec.ECDH(), client_public_key)

    # Derive keys from the shared secret using HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(shared_secret)

    server_public_key = private_key.public_key()
    server_public_key_pem = server_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return jsonify({
        'server_public_key': base64.b64encode(server_public_key_pem).decode('utf-8')
    }), 200

import logging

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not authenticate_user(username, password):
        logging.error(f"Failed login attempt for {username}")
        return jsonify({"message": "Login failed", "authenticated": False}), 401
    return jsonify({"message": "Login successful", "authenticated": True}), 200


@app.route('/add_money', methods=['POST'])
def add_money():
    username = request.json.get('username')
    amount = request.json.get('amount')
    add_funds(username, amount)
    return jsonify({"message": f"Added {amount} to {username}'s account"}), 200

@app.route('/withdraw_money', methods=['POST'])
def withdraw_money():
    username = request.json.get('username')
    amount = request.json.get('amount')
    remove_funds(username, amount)
    return jsonify({"message": f"Withdrew {amount} from {username}'s account"}), 200

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

@app.route('/download_audit_log', methods=['GET'])
def download_audit_log():
    filepath = os.path.join(os.getcwd(), "transaction_log.txt")
    try:
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        return "File not found.", 404

@app.route('/logout', methods=['GET'])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
