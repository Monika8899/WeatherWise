import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import uuid
import os

# Import the module that contains your functions
import database

class TestDatabaseModule(unittest.TestCase):
    
    def setUp(self):
        """Set up common test fixtures."""
        # Create patch for UUID to ensure consistent test results
        self.uuid_patch = patch('uuid.uuid4')
        self.mock_uuid = self.uuid_patch.start()
        self.mock_uuid.return_value = "test-uuid-1234"
        
    def tearDown(self):
        """Clean up after tests."""
        self.uuid_patch.stop()
    
    @patch('database.connect_db')
    def test_init_db_success(self, mock_connect_db):
        """Test successful database initialization."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        result = database.init_db()
        
        # Assertions
        self.assertTrue(result)
        mock_connect_db.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 3)  # 3 CREATE TABLE statements
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_init_db_failure_connection(self, mock_connect_db):
        """Test database initialization when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.init_db()
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_init_db_failure_execution(self, mock_connect_db):
        """Test database initialization when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.init_db()
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_or_create_user_existing(self, mock_connect_db):
        """Test retrieving an existing user."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to return an existing user
        mock_cursor.fetchone.return_value = (123, "existing-uuid")
        
        # Call the function
        result = database.get_or_create_user("testuser")
        
        # Assertions
        self.assertEqual(result, {"id": 123, "username": "testuser", "unique_id": "existing-uuid"})
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "SELECT id, unique_id FROM users WHERE username = %s", 
            ("testuser",)
        )
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_or_create_user_new(self, mock_connect_db):
        """Test creating a new user."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to return None for existing user, then user ID for new user
        mock_cursor.fetchone.side_effect = [None, (456,)]
        
        # Call the function
        result = database.get_or_create_user("newuser")
        
        # Assertions
        self.assertEqual(result, {"id": 456, "username": "newuser", "unique_id": "test-uuid-1234"})
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_or_create_user_connection_failure(self, mock_connect_db):
        """Test user creation/retrieval when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.get_or_create_user("testuser")
        
        # Assertions
        self.assertIsNone(result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_or_create_user_execution_error(self, mock_connect_db):
        """Test user creation/retrieval when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.get_or_create_user("testuser")
        
        # Assertions
        self.assertIsNone(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_save_weather_data_success(self, mock_connect_db):
        """Test successfully saving weather data."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        result = database.save_weather_data("Portland", 22.5, "Sunny")
        
        # Assertions
        self.assertTrue(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO weather_history (city, temperature, condition) VALUES (%s, %s, %s)",
            ("Portland", 22.5, "Sunny")
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_save_weather_data_connection_failure(self, mock_connect_db):
        """Test saving weather data when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.save_weather_data("Portland", 22.5, "Sunny")
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_save_weather_data_execution_error(self, mock_connect_db):
        """Test saving weather data when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.save_weather_data("Portland", 22.5, "Sunny")
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_temperature_trends_recent(self, mock_connect_db):
        """Test retrieving recent temperature trends."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock return data
        expected_data = [
            ('2025-02-20', 22.5, 18.2, 26.8, 'Sunny, Clear'),
            ('2025-02-21', 24.1, 19.5, 27.3, 'Partly Cloudy'),
            ('2025-02-22', 21.8, 17.9, 25.4, 'Cloudy')
        ]
        mock_cursor.fetchall.return_value = expected_data
        
        # Call the function
        result = database.get_temperature_trends('Portland', days=3, seasonal=False)
        
        # Assertions
        self.assertEqual(result, expected_data)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_temperature_trends_seasonal(self, mock_connect_db):
        """Test retrieving seasonal temperature trends."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock return data
        expected_data = [
            ('2024-02-20', 20.5, 16.2, 24.8, 'Sunny'),
            ('2023-02-21', 21.1, 17.5, 25.3, 'Clear'),
            ('2022-02-22', 19.8, 15.9, 23.4, 'Cloudy')
        ]
        mock_cursor.fetchall.return_value = expected_data
        
        # Call the function
        result = database.get_temperature_trends('Portland', seasonal=True)
        
        # Assertions
        self.assertEqual(result, expected_data)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_add_user_city_success(self, mock_connect_db):
        """Test successfully adding a city for a user."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        result = database.add_user_city(123, "Portland")
        
        # Assertions
        self.assertTrue(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO user_cities (user_id, city) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (123, "Portland")
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_add_user_city_connection_failure(self, mock_connect_db):
        """Test adding a city when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.add_user_city(123, "Portland")
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_add_user_city_execution_error(self, mock_connect_db):
        """Test adding a city when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.add_user_city(123, "Portland")
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_user_cities_success(self, mock_connect_db):
        """Test successfully retrieving cities for a user."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock return data
        mock_cursor.fetchall.return_value = [("Portland",), ("Seattle",), ("San Francisco",)]
        
        # Call the function
        result = database.get_user_cities(123)
        
        # Assertions
        self.assertEqual(result, ["Portland", "Seattle", "San Francisco"])
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "SELECT city FROM user_cities WHERE user_id = %s ORDER BY created_at DESC",
            (123,)
        )
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_user_cities_connection_failure(self, mock_connect_db):
        """Test retrieving cities when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.get_user_cities(123)
        
        # Assertions
        self.assertEqual(result, [])
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_get_user_cities_execution_error(self, mock_connect_db):
        """Test retrieving cities when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.get_user_cities(123)
        
        # Assertions
        self.assertEqual(result, [])
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_remove_user_city_success(self, mock_connect_db):
        """Test successfully removing a city for a user."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        result = database.remove_user_city(123, "Portland")
        
        # Assertions
        self.assertTrue(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM user_cities WHERE user_id = %s AND city = %s",
            (123, "Portland")
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_remove_user_city_connection_failure(self, mock_connect_db):
        """Test removing a city when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.remove_user_city(123, "Portland")
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_remove_user_city_execution_error(self, mock_connect_db):
        """Test removing a city when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.remove_user_city(123, "Portland")
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_cleanup_old_data_success(self, mock_connect_db):
        """Test successfully cleaning up old data."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        result = database.cleanup_old_data(days=30)
        
        # Assertions
        self.assertTrue(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_cleanup_old_data_connection_failure(self, mock_connect_db):
        """Test cleaning up old data when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.cleanup_old_data(days=30)
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_cleanup_old_data_execution_error(self, mock_connect_db):
        """Test cleaning up old data when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Call the function
        result = database.cleanup_old_data(days=30)
        
        # Assertions
        self.assertFalse(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_check_db_health_success(self, mock_connect_db):
        """Test successfully checking database health."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock return data
        mock_cursor.fetchall.side_effect = [
            [("users",), ("weather_history",), ("user_cities",)],  # Tables
        ]
        mock_cursor.fetchone.side_effect = [(10,), (100,), (50,)]  # Record counts
        
        # Call the function
        result = database.check_db_health()
        
        # Assertions
        expected_result = {
            "status": "healthy",
            "tables": ["users", "weather_history", "user_cities"],
            "record_counts": {
                "users": 10,
                "weather_history": 100,
                "user_cities": 50
            }
        }
        self.assertEqual(result, expected_result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 4)  # 1 for tables, 3 for counts
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_check_db_health_connection_failure(self, mock_connect_db):
        """Test checking database health when connection fails."""
        # Setup mock to return None (connection failure)
        mock_connect_db.return_value = None
        
        # Call the function
        result = database.check_db_health()
        
        # Assertions
        expected_result = {"status": "error", "message": "Cannot connect to database"}
        self.assertEqual(result, expected_result)
        mock_connect_db.assert_called_once()
    
    @patch('database.connect_db')
    def test_check_db_health_execution_error(self, mock_connect_db):
        """Test checking database health when execution fails."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        error_message = "Database error"
        mock_cursor.execute.side_effect = Exception(error_message)
        
        # Call the function
        result = database.check_db_health()
        
        # Assertions
        expected_result = {"status": "error", "message": error_message}
        self.assertEqual(result, expected_result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('database.connect_db')
    def test_add_test_historical_data_success(self, mock_connect_db):
        """Test successfully adding test historical data."""
        # Setup mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        result = database.add_test_historical_data("Portland", 25.0)
        
        # Assertions
        self.assertTrue(result)
        mock_connect_db.assert_called_once()
        mock_conn.cursor.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 7)  # 7 days of data
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('database.connect_db')
    def test_connect_db(self, mock_connect_psycopg2):
        """Test the connect_db function with success case."""
        # Setup mock psycopg2 connection
        mock_conn = MagicMock()
        mock_connect_psycopg2.return_value = mock_conn
        
        # Test with successful connection
        result = database.connect_db()
        self.assertEqual(result, mock_conn)
        mock_connect_psycopg2.assert_called_once()

    @patch('database.psycopg2.connect')
    def test_connect_db_exception(self, mock_connect):
        """Test the connect_db function with exception case."""
        # Setup mock to raise exception
        mock_connect.side_effect = Exception("Connection error")
        
        # Test with failed connection
        result = database.connect_db()
        self.assertIsNone(result)
        mock_connect.assert_called_once()

if __name__ == '__main__':
    unittest.main()