import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None


def init_db():
    """Initialize database with all required tables."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to initialize database - connection failed")
        return False

    cursor = conn.cursor()
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                unique_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Weather history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id SERIAL PRIMARY KEY,
                city TEXT NOT NULL,
                temperature FLOAT NOT NULL,
                condition TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # User cities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cities (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                city TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, city)
            )
        ''')


        conn.commit()
        logger.info("Database initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def get_or_create_user(username):
    """Get existing user or create new one with unique ID."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return None

    cursor = conn.cursor()
    try:
        # Try to get existing user
        cursor.execute("SELECT id, unique_id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            user_id, unique_id = user
            logger.info(f"Found existing user: {username}")
        else:
            # Create new user with unique ID
            unique_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (username, unique_id) VALUES (%s, %s) RETURNING id",
                (username, unique_id)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"Created new user: {username}")

        return {"id": user_id, "username": username, "unique_id": unique_id}

    except Exception as e:
        logger.error(f"Error in get_or_create_user: {e}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        conn.close()


def save_weather_data(city, temperature, condition):
    """Store weather data for analytics."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO weather_history (city, temperature, condition) VALUES (%s, %s, %s)",
            (city, temperature, condition)
        )
        conn.commit()
        logger.info(f"Saved weather data for {city}")
        return True

    except Exception as e:
        logger.error(f"Error saving weather data: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def get_temperature_trends(city, days=7):
    """Get temperature trends for a city."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                DATE(recorded_at) as date,
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                STRING_AGG(DISTINCT condition, ', ') as conditions
            FROM weather_history
            WHERE city = %s
            AND recorded_at >= %s
            GROUP BY DATE(recorded_at)
            ORDER BY DATE(recorded_at)
        """, (city, datetime.now() - timedelta(days=days)))

        trends = cursor.fetchall()
        logger.info(f"Retrieved temperature trends for {city}")
        return trends

    except Exception as e:
        logger.error(f"Error getting temperature trends: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def add_user_city(user_id, city):
    """Add a city to user's saved cities."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_cities (user_id, city) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (user_id, city)
        )
        conn.commit()
        logger.info(f"Added city {city} for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error adding user city: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def get_user_cities(user_id):
    """Get list of cities saved by user."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return []

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT city FROM user_cities WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        cities = [row[0] for row in cursor.fetchall()]
        logger.info(f"Retrieved cities for user {user_id}")
        return cities

    except Exception as e:
        logger.error(f"Error getting user cities: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def remove_user_city(user_id, city):
    """Remove a city from user's saved cities."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM user_cities WHERE user_id = %s AND city = %s",
            (user_id, city)
        )
        conn.commit()
        logger.info(f"Removed city {city} for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error removing user city: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def cleanup_old_data(days=30):
    """Clean up weather history older than specified days."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM weather_history WHERE recorded_at < %s",
            (datetime.now() - timedelta(days=days),)
        )
        conn.commit()
        logger.info(f"Cleaned up weather data older than {days} days")
        return True

    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


# Function to check database health
def check_db_health():
    """Check database connection and table status."""
    conn = connect_db()
    if not conn:
        return {"status": "error", "message": "Cannot connect to database"}

    cursor = conn.cursor()
    try:
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        # Check record counts
        stats = {}
        for table in table_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count

        return {
            "status": "healthy",
            "tables": table_names,
            "record_counts": stats
        }

    except Exception as e:
        logger.error(f"Database health check error: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        cursor.close()
        conn.close()

def add_test_historical_data(city, current_temp):
    """Add sample historical data for testing alerts."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        # Add historical data entries with temperatures different from current
        for i in range(7):
            past_date = datetime.now() - timedelta(days=i+1)
            # Make historical temperatures 10°C lower than current
            historical_temp = current_temp - 10
            cursor.execute(
                "INSERT INTO weather_history (city, temperature, condition, recorded_at) VALUES (%s, %s, %s, %s)",
                (city, historical_temp, "clear", past_date)
            )
        
        conn.commit()
        logger.info(f"Added test historical data for {city}")
        return True

    except Exception as e:
        logger.error(f"Error adding test historical data: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


# If running this file directly, initialize the database
if __name__ == "__main__":
    if init_db():
        print("Database initialized successfully!")
        health_status = check_db_health()
        print("\nDatabase Health Status:")
        print(f"Status: {health_status['status']}")
        if 'tables' in health_status:
            print("\nTables:")
            for table, count in health_status['record_counts'].items():
                print(f"- {table}: {count} records")
    else:
        print("Database initialization failed!")