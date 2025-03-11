import os
import sqlite3
from database import init_db, check_db_health, get_or_create_user, add_user_city, get_user_cities


def test_sqlite_setup():
    """Test SQLite database setup and basic operations."""
    print("Testing SQLite Database Setup")
    print("-" * 50)

    # 1. Test database initialization
    print("\n1. Testing database initialization...")
    if init_db():
        print("✅ Database initialization successful!")
    else:
        print("❌ Database initialization failed!")
        return

    # 2. Check database health
    print("\n2. Checking database health...")
    health = check_db_health()
    print(f"Status: {health['status']}")
    if health['status'] == 'healthy':
        print("Tables in database:")
        for table, count in health['record_counts'].items():
            print(f"  - {table}: {count} records")

    # 3. Test user creation
    print("\n3. Testing user creation...")
    username = "test_user"
    user = get_or_create_user(username)
    if user:
        print(f"✅ User created/retrieved: ID={user['id']}, Username={user['username']}")
        user_id = user['id']
    else:
        print("❌ User creation failed!")
        return

    # 4. Test adding favorite cities
    print("\n4. Testing favorite cities...")
    test_cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
    for city in test_cities:
        success, message = add_user_city(user_id, city)
        print(f"  - Adding {city}: {'✅ Success' if success else '❌ Failed'} - {message}")

    # 5. Test retrieving cities
    print("\n5. Testing city retrieval...")
    cities = get_user_cities(user_id)
    if cities:
        print(f"Retrieved {len(cities)} cities:")
        for city in cities:
            print(f"  - {city}")
    else:
        print("No cities found or retrieval failed.")

    print("\nSQLite database setup test completed!")


if __name__ == "__main__":
    test_sqlite_setup()