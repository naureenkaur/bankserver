import sqlite3
import hashlib
import os
import secrets

# Function to create the SQLite database and table
def create_database():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password_hash TEXT,
                  encryption_key BLOB,
                  mac_key BLOB)''')
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
    return secrets.token_bytes(16)  # 128-bit encryption key

# Function to generate MAC key
def generate_mac_key():
    return secrets.token_bytes(16)  # 128-bit MAC key

# Function to initialize the database with predefined users
def initialize_database():
    predefined_users = [('Alice', 'password123'), ('Bob', 'password123'), ('Charlie', 'password123')]
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    for username, password in predefined_users:
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        encryption_key = generate_encryption_key()
        mac_key = generate_mac_key()
        c.execute('''INSERT INTO users (username, password_hash, encryption_key, mac_key)
                     VALUES (?, ?, ?, ?)''', (username, password_hash, encryption_key, mac_key))
    conn.commit()
    conn.close()

# Function to authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''SELECT password_hash FROM users WHERE username=?''', (username,))
    result = c.fetchone()
    if result:
        stored_password_hash = result[0]
        # Retrieve salt from stored password hash
        salt = stored_password_hash[:16]
        # Hash the provided password with the retrieved salt
        provided_password_hash = hash_password(password, salt)
        # Compare the stored password hash with the hash of the provided password
        if stored_password_hash == provided_password_hash:
            return True
    return False

# Main function
def main():
    create_database()
    initialize_database()

    # Authenticate the predefined users
    users = ['Alice', 'Bob', 'Charlie']
    for user in users:
        if authenticate_user(user, 'password123'):  # Assuming password for all predefined users is 'password123'
            print(f"Authentication successful for user: {user}")
        else:
            print(f"Authentication failed for user: {user}")

if __name__ == "__main__":
    main()
