import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Railway PostgreSQL connection URL
DB_URL = os.getenv("RAILWAY_DB_URL")

def init_db():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def add_city(city_name):
    """Add a new city to the database."""
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cities (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (city_name,))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

def get_cities():
    """Retrieve all saved cities from the database."""
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM cities")
    cities = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return cities

if __name__ == "__main__":
    init_db()
    add_city("London")
    print("Saved cities:", get_cities())
