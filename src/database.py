import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DB_URL = os.getenv("RAILWAY_DB_URL")

if not DB_URL:
    raise ValueError("Database URL not found in environment variables!")

def connect_db():
    """Establish a secure connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(DB_URL)
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database with required tables."""
    conn = connect_db()
    if not conn:
        return False

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    unique_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_history (
                    id SERIAL PRIMARY KEY,
                    city TEXT NOT NULL,
                    temperature FLOAT NOT NULL,
                    condition TEXT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_cities (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    city TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, city)
                )
            """)

            logger.info("Database initialized successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"Database initialization error: {e}")
            return False

def get_or_create_user(username: str):
    """Retrieve existing user or create a new one."""
    conn = connect_db()
    if not conn:
        return None

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("SELECT id, unique_id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                return {"id": user[0], "username": username, "unique_id": user[1]}

            unique_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO users (username, unique_id) VALUES (%s, %s) RETURNING id", (username, unique_id))
            user_id = cursor.fetchone()[0]
            conn.commit()

            logger.info(f"New user created: {username}")
            return {"id": user_id, "username": username, "unique_id": unique_id}
        except psycopg2.Error as e:
            logger.error(f"Error in get_or_create_user: {e}")
            return None

def save_weather_data(city: str, temperature: float, condition: str) -> bool:
    """Store weather data efficiently."""
    conn = connect_db()
    if not conn:
        return False

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO weather_history (city, temperature, condition) VALUES (%s, %s, %s)",
                (city.lower(), temperature, condition),
            )
            conn.commit()
            logger.info(f"Weather data saved for {city}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error saving weather data: {e}")
            return False

def get_temperature_trends(city: str, days: int = 7):
    """Retrieve temperature trends for a city."""
    conn = connect_db()
    if not conn:
        return []

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT DATE(recorded_at), AVG(temperature), MIN(temperature), MAX(temperature), STRING_AGG(DISTINCT condition, ', ')
                FROM weather_history
                WHERE city = %s AND recorded_at >= %s
                GROUP BY DATE(recorded_at)
                ORDER BY DATE(recorded_at)
            """, (city, datetime.now() - timedelta(days=days)))

            return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error retrieving temperature trends: {e}")
            return []

def add_user_city(user_id: int, city: str) -> bool:
    """Add a city to user's saved list."""
    conn = connect_db()
    if not conn:
        return False

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO user_cities (user_id, city) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, city))
            conn.commit()
            return True
        except psycopg2.Error as e:
            logger.error(f"Error adding user city: {e}")
            return False

def get_user_cities(user_id: int) -> List[str]:
    """Retrieve user's saved cities."""
    conn = connect_db()
    if not conn:
        return []

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("SELECT DISTINCT INITCAP(city) FROM user_cities WHERE user_id = %s ORDER BY city", (user_id,))
            return [row[0] for row in cursor.fetchall()]
        except psycopg2.Error as e:
            logger.error(f"Error getting user cities: {e}")
            return []

def remove_user_city(user_id: int, city: str) -> bool:
    """Remove a saved city from the user's list."""
    conn = connect_db()
    if not conn:
        return False

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM user_cities WHERE user_id = %s AND city = %s", (user_id, city))
            conn.commit()
            return True
        except psycopg2.Error as e:
            logger.error(f"Error removing user city: {e}")
            return False

def cleanup_old_data(days: int = 30) -> bool:
    """Remove weather history older than specified days."""
    conn = connect_db()
    if not conn:
        return False

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("DELETE FROM weather_history WHERE recorded_at < %s", (datetime.now() - timedelta(days=days),))
            conn.commit()
            logger.info(f"Cleaned up weather data older than {days} days")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False

def check_db_health():
    """Check database health by listing tables and record counts."""
    conn = connect_db()
    if not conn:
        return {"status": "error", "message": "Cannot connect to database"}

    with conn, conn.cursor() as cursor:
        try:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [table[0] for table in cursor.fetchall()]

            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]

            return {"status": "healthy", "tables": tables, "record_counts": stats}
        except psycopg2.Error as e:
            logger.error(f"Database health check error: {e}")
            return {"status": "error", "message": str(e)}

# Run database initialization when script is executed directly
if __name__ == "__main__":
    if init_db():
        print("✅ Database initialized successfully!")
    else:
        print("❌ Database initialization failed!")