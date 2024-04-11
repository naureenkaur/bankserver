from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import sqlite3
import hashlib
import os
# import authentication functions from database.py
from database import authenticate_user, add_funds, remove_funds

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

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
    username = request.json.get('username')
    amount = request.json.get('amount')
    add_funds(username, amount)
    return jsonify({"message": f"Added {amount} to {username}'s account"}), 200

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