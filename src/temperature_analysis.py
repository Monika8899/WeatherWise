import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_date_range(current_date=None, window_days=15):
    """
    Calculate date range for seasonal temperature analysis.
    
    Args:
        current_date (datetime): Reference date (defaults to today)
        window_days (int): Number of days before/after to include
    
    Returns:
        tuple: (month, day_start, day_end, month_condition, prev_month, next_month)
    """
    if current_date is None:
        current_date = datetime.now()
        
    month = current_date.month
    day_start = current_date.day - window_days
    day_end = current_date.day + window_days
    
    # Default month condition
    month_condition = f"EXTRACT(MONTH FROM recorded_at) = {month}"
    prev_month = None
    next_month = None
    
    # Handle start of month boundary
    if day_start <= 0:
        prev_month = 12 if month == 1 else month - 1
        month_condition = f"(EXTRACT(MONTH FROM recorded_at) = {month} OR " + \
                         f"(EXTRACT(MONTH FROM recorded_at) = {prev_month} AND EXTRACT(DAY FROM recorded_at) >= {31 + day_start}))"
        day_start = 1
    
    # Handle end of month boundary
    if day_end > 31:
        next_month = 1 if month == 12 else month + 1
        month_condition = f"(EXTRACT(MONTH FROM recorded_at) = {month} OR " + \
                         f"(EXTRACT(MONTH FROM recorded_at) = {next_month} AND EXTRACT(DAY FROM recorded_at) <= {day_end - 31}))"
        day_end = 31
    
    return (month, day_start, day_end, month_condition, prev_month, next_month)

def build_recent_query():
    """Build SQL query for recent temperature trends."""
    return """
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
    """

def build_seasonal_query(month_condition):
    """Build SQL query for seasonal temperature trends."""
    return f"""
        SELECT 
            DATE(recorded_at) as date,
            AVG(temperature) as avg_temp,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            STRING_AGG(DISTINCT condition, ', ') as conditions
        FROM weather_history
        WHERE city = %s
        AND {month_condition}
        AND EXTRACT(DAY FROM recorded_at) BETWEEN %s AND %s
        AND recorded_at < %s
        GROUP BY DATE(recorded_at)
        ORDER BY DATE(recorded_at)
    """

def get_temperature_trends(city, days=7, seasonal=True, db_connector=None):
    """
    Get temperature trends for a city.
    
    Args:
        city (str): City name to get trends for
        days (int): Number of days to look back for recent trends
        seasonal (bool): If True, look at same calendar period in previous years
        db_connector (function): Function to get database connection (for testing)
    
    Returns:
        list: List of tuples with temperature trend data
    """
    # Allow dependency injection for testing
    if db_connector is None:
        from database import connect_db
        db_connector = connect_db
    
    conn = db_connector()
    if not conn:
        logger.error("Failed to connect to database")
        return []

    cursor = conn.cursor()
    try:
        if seasonal:
            # Get seasonal date range
            _, day_start, day_end, month_condition, _, _ = calculate_date_range()
            
            # Build and execute seasonal query
            query = build_seasonal_query(month_condition)
            cursor.execute(query, (city, day_start, day_end, datetime.now() - timedelta(days=1)))
        else:
            # Build and execute recent query
            query = build_recent_query()
            cursor.execute(query, (city, datetime.now() - timedelta(days=days)))

        trends = cursor.fetchall()
        logger.info(f"Retrieved temperature trends for {city}")
        return trends

    except Exception as e:
        logger.error(f"Error getting temperature trends: {e}")
        return []

    finally:
        cursor.close()
        conn.close()