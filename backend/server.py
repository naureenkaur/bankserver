from flask import Flask, request, jsonify
from datetime import datetime
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import encryption
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# Dictionary to store account information (username, password, balance)
accounts = {'Alice': {'password': 'password123', 'balance': 1000},
            'Bob': {'password': 'securepwd', 'balance': 500},
            'Eve': {'password': 'password', 'balance': 2000}}

user_salts = {
    'Alice': 'somerandomsalt1',
    'Bob': 'somerandomsalt2',
    'Eve': 'somerandomsalt3'
}

@app.route('/get_salt', methods=['GET'])
def get_salt():
    username = request.args.get('username')
    if username and username in user_salts:
        salt = user_salts[username]
        return jsonify({'salt': salt})
    else:
        return jsonify({'message': 'User not found'}), 404
    
# Path to the audit log file
AUDIT_LOG_FILE = "audit_log.txt"

def log_transaction(username, action, amount):
    """
    Log the transaction information into an audit log file.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG_FILE, "a") as file:
        file.write(f"Username: {username}, Action: {action}, Amount: {amount}, Time: {now} \n")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    hashed_password = data.get('password')
    mac_received = data.get('mac')

    if None in (username, hashed_password, mac_received):
        return jsonify({'message': 'Missing data in request', 'authenticated': False}), 400

    # Assume encryption and verification functions exist
    # Your logic to verify username, password, and mac
    return jsonify({'message': 'Login successful', 'authenticated': True})

@app.route('/transaction/deposit', methods=['POST'])
def deposit():
    encrypted_data = request.json['encryptedData']
    mac_received = request.json['hmac']

    if not encryption.verify_mac(encrypted_data, mac_received):
        return jsonify({'message': 'MAC verification failed'}), 403

    data = encryption.decrypt(encrypted_data)
    username = data['username']
    amount = float(data['amount'])

    if username in accounts:
        accounts[username]['balance'] += amount
        log_transaction(username, 'deposit', amount)
        return jsonify({'message': 'Deposit successful', 'new_balance': accounts[username]['balance']})
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/transaction/withdraw', methods=['POST'])
def withdraw():
    encrypted_data = request.json['encryptedData']
    mac_received = request.json['hmac']

    if not encryption.verify_mac(encrypted_data, mac_received):
        return jsonify({'message': 'MAC verification failed'}), 403

    data = encryption.decrypt(encrypted_data)
    username = data['username']
    amount = float(data['amount'])

    if username in accounts and accounts[username]['balance'] >= amount:
        accounts[username]['balance'] -= amount
        log_transaction(username, 'withdraw', amount)
        return jsonify({'message': 'Withdrawal successful', 'new_balance': accounts[username]['balance']})
    else:
        return jsonify({'message': 'Insufficient funds'}), 403

@app.route('/balance/<username>', methods=['GET'])
def check_balance(username):
    if username in accounts:
        balance = accounts[username]['balance']
        return jsonify({'balance': balance})
    else:
        return jsonify({'message': 'User not found'}), 404
    

if __name__ == '__main__':
    app.run(debug=True)
