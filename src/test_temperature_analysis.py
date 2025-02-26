import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import temperature_analysis

class TestTemperatureAnalysis(unittest.TestCase):
    
    def test_calculate_date_range_normal(self):
        """Test normal date calculation (middle of month)."""
        test_date = datetime(2025, 3, 15)
        month, day_start, day_end, month_condition, prev_month, next_month = (
            temperature_analysis.calculate_date_range(test_date)
        )
        
        self.assertEqual(month, 3)
        self.assertEqual(day_start, 0)  # 15 - 15 = 0, should be adjusted to 1
        self.assertEqual(day_end, 30)  # 15 + 15 = 30
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 3" in month_condition)
        self.assertEqual(prev_month, 2)  # February
        self.assertIsNone(next_month)  # No next month needed
    
    def test_calculate_date_range_start_of_month(self):
        """Test date calculation at start of month."""
        test_date = datetime(2025, 3, 5)
        month, day_start, day_end, month_condition, prev_month, next_month = (
            temperature_analysis.calculate_date_range(test_date)
        )
        
        self.assertEqual(month, 3)
        self.assertEqual(day_start, 1)  # Adjusted from -10
        self.assertEqual(day_end, 20)
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 3" in month_condition)
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 2" in month_condition)
        self.assertEqual(prev_month, 2)  # February
        self.assertIsNone(next_month)
    
    def test_calculate_date_range_end_of_month(self):
        """Test date calculation at end of month."""
        test_date = datetime(2025, 3, 25)
        month, day_start, day_end, month_condition, prev_month, next_month = (
            temperature_analysis.calculate_date_range(test_date)
        )
        
        self.assertEqual(month, 3)
        self.assertEqual(day_start, 10)
        self.assertEqual(day_end, 31)  # Adjusted from 40
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 3" in month_condition)
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 4" in month_condition)
        self.assertIsNone(prev_month)
        self.assertEqual(next_month, 4)  # April
    
    def test_calculate_date_range_year_boundary(self):
        """Test date calculation at year boundary (December/January)."""
        # December 25
        test_date = datetime(2025, 12, 25)
        month, day_start, day_end, month_condition, prev_month, next_month = (
            temperature_analysis.calculate_date_range(test_date)
        )
        
        self.assertEqual(month, 12)
        self.assertEqual(day_start, 10)
        self.assertEqual(day_end, 31)  # Adjusted from 40
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 12" in month_condition)
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 1" in month_condition)
        self.assertIsNone(prev_month)
        self.assertEqual(next_month, 1)  # January
        
        # January 5
        test_date = datetime(2025, 1, 5)
        month, day_start, day_end, month_condition, prev_month, next_month = (
            temperature_analysis.calculate_date_range(test_date)
        )
        
        self.assertEqual(month, 1)
        self.assertEqual(day_start, 1)  # Adjusted from -10
        self.assertEqual(day_end, 20)
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 1" in month_condition)
        self.assertTrue("EXTRACT(MONTH FROM recorded_at) = 12" in month_condition)
        self.assertEqual(prev_month, 12)  # December
        self.assertIsNone(next_month)
    
    def test_build_recent_query(self):
        """Test SQL query generation for recent data."""
        query = temperature_analysis.build_recent_query()
        
        # Check that query contains essential elements
        self.assertIn("SELECT", query)
        self.assertIn("FROM weather_history", query)
        self.assertIn("WHERE city = %s", query)
        self.assertIn("AND recorded_at >= %s", query)
        self.assertIn("GROUP BY DATE(recorded_at)", query)
        self.assertIn("ORDER BY DATE(recorded_at)", query)
    
    def test_build_seasonal_query(self):
        """Test SQL query generation for seasonal data."""
        month_condition = "EXTRACT(MONTH FROM recorded_at) = 3"
        query = temperature_analysis.build_seasonal_query(month_condition)
        
        # Check that query contains essential elements
        self.assertIn("SELECT", query)
        self.assertIn("FROM weather_history", query)
        self.assertIn("WHERE city = %s", query)
        self.assertIn(month_condition, query)
        self.assertIn("AND EXTRACT(DAY FROM recorded_at) BETWEEN %s AND %s", query)
        self.assertIn("AND recorded_at < %s", query)
        self.assertIn("GROUP BY DATE(recorded_at)", query)
        self.assertIn("ORDER BY DATE(recorded_at)", query)
    
    def test_get_temperature_trends_recent(self):
        """Test retrieving recent temperature trends."""
        # Create mock database connector and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock return data
        expected_data = [
            ('2025-02-20', 22.5, 18.2, 26.8, 'Sunny, Clear'),
            ('2025-02-21', 24.1, 19.5, 27.3, 'Partly Cloudy'),
            ('2025-02-22', 21.8, 17.9, 25.4, 'Cloudy')
        ]
        mock_cursor.fetchall.return_value = expected_data
        
        # Create mock db_connector function
        mock_db_connector = MagicMock(return_value=mock_conn)
        
        # Call the function
        result = temperature_analysis.get_temperature_trends(
            'Portland', days=3, seasonal=False, db_connector=mock_db_connector
        )
        
        # Assertions
        self.assertEqual(result, expected_data)
        mock_db_connector.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # Verify SQL parameters
        args = mock_cursor.execute.call_args[0]
        self.assertEqual(args[1][0], 'Portland')  # First parameter should be city
        self.assertIsInstance(args[1][1], datetime)  # Second parameter should be a date
        
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('temperature_analysis.datetime')
    def test_get_temperature_trends_seasonal(self, mock_datetime):
        """Test retrieving seasonal temperature trends."""
        # Setup fixed datetime for testing
        mock_now = datetime(2025, 3, 15)
        mock_datetime.now.return_value = mock_now
        
        # Create mock database connector and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock return data
        expected_data = [
            ('2024-03-10', 20.5, 16.2, 24.8, 'Sunny'),
            ('2023-03-12', 21.1, 17.5, 25.3, 'Clear'),
            ('2022-03-14', 19.8, 15.9, 23.4, 'Cloudy')
        ]
        mock_cursor.fetchall.return_value = expected_data
        
        # Create mock db_connector function
        mock_db_connector = MagicMock(return_value=mock_conn)
        
        # Call the function
        result = temperature_analysis.get_temperature_trends(
            'Portland', seasonal=True, db_connector=mock_db_connector
        )
        
        # Assertions
        self.assertEqual(result, expected_data)
        mock_db_connector.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        
        # For seasonal queries, verify parameters
        args = mock_cursor.execute.call_args[0]
        self.assertEqual(args[1][0], 'Portland')  # First parameter should be city
        
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_get_temperature_trends_db_connection_failure(self):
        """Test behavior when database connection fails."""
        # Create mock db_connector that returns None (connection failure)
        mock_db_connector = MagicMock(return_value=None)
        
        # Call the function
        result = temperature_analysis.get_temperature_trends(
            'Portland', db_connector=mock_db_connector
        )
        
        # Assertions
        self.assertEqual(result, [])  # Should return empty list on connection failure
        mock_db_connector.assert_called_once()
    
    def test_get_temperature_trends_query_error(self):
        """Test behavior when query execution fails."""
        # Create mock database connector and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup mock to raise an exception during execute
        mock_cursor.execute.side_effect = Exception("Database error")
        
        # Create mock db_connector function
        mock_db_connector = MagicMock(return_value=mock_conn)
        
        # Call the function
        result = temperature_analysis.get_temperature_trends(
            'Portland', db_connector=mock_db_connector
        )
        
        # Assertions
        self.assertEqual(result, [])  # Should return empty list on execution error
        mock_db_connector.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('temperature_analysis.logger')
    def test_logging(self, mock_logger):
        """Test that appropriate logging occurs."""
        # Create mock database connector and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Create mock db_connector function for success case
        mock_db_connector = MagicMock(return_value=mock_conn)
        
        # Call the function - success case
        temperature_analysis.get_temperature_trends(
            'Portland', db_connector=mock_db_connector
        )
        
        # Verify logger.info was called with appropriate message
        mock_logger.info.assert_called_with("Retrieved temperature trends for Portland")
        
        # Create mock db_connector for connection failure
        mock_db_connector_fail = MagicMock(return_value=None)
        
        # Call the function - connection failure
        temperature_analysis.get_temperature_trends(
            'Seattle', db_connector=mock_db_connector_fail
        )
        
        # Verify logger.error was called
        mock_logger.error.assert_called_with("Failed to connect to database")
        
        # Setup for execution error
        mock_cursor.execute.side_effect = Exception("Query failed")
        
        # Call the function - execution error
        temperature_analysis.get_temperature_trends(
            'Chicago', db_connector=mock_db_connector
        )
        
        # Verify error logging
        mock_logger.error.assert_called_with("Error getting temperature trends: Query failed")

if __name__ == '__main__':
    unittest.main()