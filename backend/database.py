import sqlite3
import hashlib
import os
import secrets
from datetime import datetime

# Function to create the SQLite database and table
def create_database():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    # Create users table if it doesn't exist, now including a salt column
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password_hash TEXT,
                  encryption_key BLOB,
                  mac_key BLOB,
                  amount INTEGER,
                  salt BLOB)''')  # Added salt column
    # Create transactions table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  action TEXT,
                  amount INTEGER,
                  time TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    conn.commit()
    conn.close()

# Function to generate a random salt
def generate_salt():
    return os.urandom(16)

# Function to hash the password with salt
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

# Function to generate encryption key
def generate_encryption_key():
    return secrets.token_bytes(16)

# Function to generate MAC key
def generate_mac_key():
    return secrets.token_bytes(16)

# Function to initialize the database with predefined users, amounts, and transactions
def initialize_database():
    predefined_users = [
        ('Alice', 'password123', 1000, []),
        ('Bob', 'securepwd', 2000, []),
        ('Charlie', 'password', 3000, [])
    ]
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    for username, password, amount, transactions in predefined_users:
        # Check if the user already exists
        c.execute('''SELECT id FROM users WHERE username=?''', (username,))
        if c.fetchone() is None:
            salt = generate_salt()
            password_hash = hash_password(password, salt)
            encryption_key = generate_encryption_key()
            mac_key = generate_mac_key()
            # Now also inserting the salt into the database
            c.execute('''INSERT INTO users (username, password_hash, encryption_key, mac_key, amount, salt) VALUES (?, ?, ?, ?, ?, ?)''',
                      (username, password_hash, encryption_key, mac_key, amount, salt))
            for transaction in transactions:
                c.execute('''INSERT INTO transactions (username, action, amount, time) VALUES (?, ?, ?, ?)''', (username, transaction['action'], transaction['amount'], transaction['time']))
        else:
            print(f"User {username} already exists, skipping insertion.")
    conn.commit()
    conn.close()

# Function to authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    # Retrieve password hash and salt for the user
    c.execute('''SELECT password_hash, salt FROM users WHERE username=?''', (username,))
    result = c.fetchone()
    if result:
        stored_password_hash, salt = result
        provided_password_hash = hash_password(password, salt)
        if stored_password_hash == provided_password_hash:
            return True
    return False

# Functions for adding funds, removing funds, logging transactions, and retrieving transaction history remain unchanged
# Function to add funds to a user's account
def add_funds(username, amount):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''UPDATE users SET amount = amount + ? WHERE username = ?''', (amount, username))
    # Log the transaction
    log_transaction(username, 'Add Funds', amount)
    conn.commit()
    conn.close()

# Function to remove funds from a user's account
def remove_funds(username, amount):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''UPDATE users SET amount = amount - ? WHERE username = ?''', (amount, username))
    # Log the transaction
    log_transaction(username, 'Remove Funds', amount)
    conn.commit()
    conn.close()

# Function to log transaction
def log_transaction(username, action, amount):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("transaction_log.txt", "a") as file:
        file.write(f"Username: {username}, Action: {action}, Amount: {amount}, Time: {now}\n")

# Function to retrieve transaction history for a user
def get_transaction_history(username):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM transactions WHERE username = ?''', (username,))
    transactions = c.fetchall()
    conn.close()
    return transactions

# Main function
# Main function
def main():
    create_database()
    initialize_database()

    # Corrected authentication checks with appropriate passwords
    predefined_users_passwords = {'Alice': 'password123', 'Bob': 'securepwd', 'Charlie': 'password'}
    for user, password in predefined_users_passwords.items():
        if authenticate_user(user, password):
            print(f"Authentication successful for user: {user}")
        else:
            print(f"Authentication failed for user: {user}")


if __name__ == "__main__":
    main()