import sqlite3
import hashlib

DB_NAME = "vania_score.db"

def init_db():
    """Initializes the database and creates necessary tables."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE NOT NULL, 
                    password TEXT NOT NULL, 
                    score INTEGER DEFAULT 0
                )''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT, 
                    score INTEGER
                )''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

# --- CREATE ---
def register_user(username, password):
    if not username or not password or len(password) < 6:
        return False, "Validation failed: Username and password is needed M8!."

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                           (username.strip(), hash_password(password)))
            conn.commit()
            return True, "K."
    except sqlite3.IntegrityError:
        return False, "Error: we found ya twin M8!!!!."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

# --- READ ---
def login_user(username, password):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            hpwd = hash_password(password)
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, hpwd))
            user = cursor.fetchone()
            return user[0] if user else None
    except sqlite3.Error as e:
        print(f"Login error: {e}")
        return None

# --- UPDATE ---
def update_user_score(user_id, new_score):
    if not isinstance(new_score, int) or new_score < 0:
        return False, "something has gone wrong M8."

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET score = ? WHERE id = ?', (new_score, user_id))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "It has passed!."
            return False, "Couldn't found y'a M8."
    except sqlite3.Error as e:
        return False, f"Update error: {e}"

# --- DELETE ---
def delete_user(user_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Account's gone M8."
            return False, "Can't kill, whats not there ^m^"
    except sqlite3.Error as e:
        return False, f"Delete error: {e}"