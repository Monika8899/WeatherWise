import os
import sqlite3
import hashlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Authentication database file
AUTH_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auth.db')


def init_auth_db():
    """Initialize the authentication database."""
    try:
        conn = sqlite3.connect(AUTH_DB_FILE)
        cursor = conn.cursor()

        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Authentication database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing authentication database: {e}")
        return False


def get_user(username):
    """Get user details from database."""
    try:
        conn = sqlite3.connect(AUTH_DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, password, name, email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return {
                "id": user[0],
                "username": user[1],
                "password": user[2],
                "name": user[3],
                "email": user[4]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


def authenticate(username, password):
    """Authenticate a user with username and password"""
    user = get_user(username)
    if user and user["password"] == hashlib.sha256(password.encode()).hexdigest():
        return True, user
    return False, None


def register_user(username, name, password, email):
    """Register a new user"""
    if get_user(username):
        return False, "Username already exists"

    try:
        conn = sqlite3.connect(AUTH_DB_FILE)
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password, name, email) VALUES (?, ?, ?, ?)",
            (username, hashed_password, name, email)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"User registered successfully: {username}")
        return True, "Registration successful"

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return False, f"Registration error: {str(e)}"


def change_password(username, current_password, new_password):
    """Change a user's password"""
    auth_success, _ = authenticate(username, current_password)
    if not auth_success:
        return False, "Current password is incorrect"

    try:
        conn = sqlite3.connect(AUTH_DB_FILE)
        cursor = conn.cursor()

        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed_password, username)
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Password updated successfully for user: {username}")
        return True, "Password updated successfully"

    except Exception as e:
        logger.error(f"Password update error: {e}")
        return False, f"Password update error: {str(e)}"


# When file is run directly, initialize the auth database
if __name__ == "__main__":
    if init_auth_db():
        print("Authentication database initialized successfully!")
    else:
        print("Failed to initialize authentication database!")