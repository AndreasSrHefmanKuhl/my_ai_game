import sqlite3
import hashlib


def init_db():
    conn = sqlite3.connect("vania_score.db")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, score INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS high_scores (id INTEGER PRIMARY KEY, username TEXT, score INTEGER)')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username,password):
    try:
        conn = sqlite3.connect("vania_score.db")
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
        conn.commit()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("vania_score.db")
    cursor = conn.cursor()
    hpwd = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hpwd))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None