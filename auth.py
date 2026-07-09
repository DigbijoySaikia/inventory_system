import hashlib
import os
import sqlite3
from database import get_connection

def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    
    pwd_bytes = password.encode('utf-8')
    hashed = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt, 100000)
    return hashed.hex(), salt.hex()

def register_user(username, password) -> tuple[bool, str]:
    if not username or not password:
        return False, "Username and password cannot be empty."
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        password_hash, salt = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_id, stored_hash, stored_salt = row
        salt_bytes = bytes.fromhex(stored_salt)
        calculated_hash, _ = hash_password(password, salt_bytes)
        if calculated_hash == stored_hash:
            return user_id
    return None