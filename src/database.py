import sqlite3
import os
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database file path
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weatherwise.db')


def connect_db():
    """Establish a connection to the SQLite database."""
    try:
        return sqlite3.connect(DB_FILE)
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                unique_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Weather history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temperature FLOAT NOT NULL,
                condition TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # User cities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                city TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, city),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
        cursor.execute("SELECT id, unique_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            user_id, unique_id = user
            logger.info(f"Found existing user: {username}")
        else:
            # Create new user with unique ID
            unique_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (username, unique_id) VALUES (?, ?)",
                (username, unique_id)
            )
            conn.commit()
            user_id = cursor.lastrowid
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
            "INSERT INTO weather_history (city, temperature, condition) VALUES (?, ?, ?)",
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


def get_user_cities(user_id):
    """Get list of cities saved by user."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return []

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT city FROM user_cities WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
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


def add_user_city(user_id, city):
    """Add a city to user's saved cities (up to 10)."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False, "Database connection error"

    cursor = conn.cursor()
    try:
        # Check if user already has 10 cities saved
        cursor.execute("SELECT COUNT(*) FROM user_cities WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]

        if count >= 10:
            return False, "Maximum limit of 10 favorite cities reached"

        # Check if city already exists for this user
        cursor.execute("SELECT 1 FROM user_cities WHERE user_id = ? AND city = ?", (user_id, city))
        if cursor.fetchone():
            return True, "City already in favorites"

        # Add the new city
        cursor.execute(
            "INSERT INTO user_cities (user_id, city) VALUES (?, ?)",
            (user_id, city)
        )
        conn.commit()
        logger.info(f"Added city {city} for user {user_id}")
        return True, "City added to favorites"

    except Exception as e:
        logger.error(f"Error adding user city: {e}")
        conn.rollback()
        return False, f"Error: {str(e)}"

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
            "DELETE FROM user_cities WHERE user_id = ? AND city = ?",
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


def get_temperature_trends(city, days=7, seasonal=True):
    """Get temperature trends for a city.

    Args:
        city (str): City name to get trends for
        days (int): Number of days to look back for recent trends
        seasonal (bool): If True, look at same calendar period in previous years
    """
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return []

    cursor = conn.cursor()
    try:
        if seasonal:
            # Get current month and day to match seasonal patterns
            current_date = datetime.now()
            month = current_date.month
            day_start = current_date.day - 15  # 15 days before current day
            day_end = current_date.day + 15  # 15 days after current day

            # Handle month boundaries
            if day_start <= 0:
                # Include previous month for negative days
                day_start = 1

            if day_end > 31:
                # Cap at end of month
                day_end = 31

            # SQLite date functions are different from PostgreSQL
            cursor.execute("""
                SELECT 
                    date(recorded_at) as date,
                    avg(temperature) as avg_temp,
                    min(temperature) as min_temp,
                    max(temperature) as max_temp,
                    group_concat(DISTINCT condition) as conditions
                FROM weather_history
                WHERE city = ?
                AND (
                    (strftime('%m', recorded_at) = ? AND 
                     strftime('%d', recorded_at) BETWEEN ? AND ?)
                )
                AND recorded_at < ?
                GROUP BY date(recorded_at)
                ORDER BY date(recorded_at)
            """, (
                city,
                str(month).zfill(2),
                str(day_start).zfill(2),
                str(day_end).zfill(2),
                (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            ))
        else:
            # Simple last N days
            cursor.execute("""
                SELECT 
                    date(recorded_at) as date,
                    avg(temperature) as avg_temp,
                    min(temperature) as min_temp,
                    max(temperature) as max_temp,
                    group_concat(DISTINCT condition) as conditions
                FROM weather_history
                WHERE city = ?
                AND recorded_at >= ?
                GROUP BY date(recorded_at)
                ORDER BY date(recorded_at)
            """, (city, (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')))

        trends = cursor.fetchall()
        logger.info(f"Retrieved temperature trends for {city}")
        return trends

    except Exception as e:
        logger.error(f"Error getting temperature trends: {e}")
        return []

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
            past_date = datetime.now() - timedelta(days=i + 1)
            # Make historical temperatures 10°C lower than current
            historical_temp = current_temp - 10
            cursor.execute(
                "INSERT INTO weather_history (city, temperature, condition, recorded_at) VALUES (?, ?, ?, ?)",
                (city, historical_temp, "clear", past_date.strftime('%Y-%m-%d %H:%M:%S'))
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


def cleanup_old_data(days=30):
    """Clean up weather history older than specified days."""
    conn = connect_db()
    if not conn:
        logger.error("Failed to connect to database")
        return False

    cursor = conn.cursor()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "DELETE FROM weather_history WHERE recorded_at < ?",
            (cutoff_date,)
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


def check_db_health():
    """Check database connection and table status."""
    conn = connect_db()
    if not conn:
        return {"status": "error", "message": "Cannot connect to database"}

    cursor = conn.cursor()
    try:
        # Check tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
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