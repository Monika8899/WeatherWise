import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch the PostgreSQL URL from the environment
DB_URL = os.getenv("RAILWAY_DB_URL")

def connect_db():
    """Establish a secure connection to the PostgreSQL database."""
    return psycopg2.connect(DB_URL)

def init_db():
    """Create tables if they don't exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            unique_id INTEGER UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_cities (
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            city TEXT NOT NULL,
            PRIMARY KEY (user_id, city)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


# Run initialization if this file is executed directly
if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully!")


def check_tables():
    """Verify if tables exist in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

if __name__ == "__main__":
    print("Existing tables:", check_tables())