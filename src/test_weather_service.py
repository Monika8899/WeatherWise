# test_weather_service.py
import pytest
from unittest.mock import patch
from weather_service import get_weather

# Mock response data for the weather API (updated structure to reflect the real response)
mock_weather_data = {
    "main": {
        "temp": 22,  # Temperature value
        "humidity": 65  # Humidity value
    },
    "wind": {
        "speed": 5  # Wind speed
    },
    "weather": [{
        "description": "clear sky"  # Weather condition
    }],
    "name": "London"
}

# Test Case 1: Basic Test for successful response
@patch('weather_service.requests.get')
def test_get_weather_success(mock_get):
    # Mock the API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_weather_data
    
    result = get_weather("London")
    
    # Check if the function returns the expected data
    assert "city" in result
    assert "temperature" in result
    assert "humidity" in result
    assert "wind_speed" in result
    assert "condition" in result
    assert result["city"] == "London"
    assert result["temperature"] == "22°C"
    assert result["humidity"] == "65%"
    assert result["wind_speed"] == "5 m/s"
    assert result["condition"] == "Clear sky"


# Test Case 2: Test for invalid city name (API response with error)
@patch('weather_service.requests.get')
def test_get_weather_invalid_city(mock_get):
    # Mock an invalid city response
    mock_get.return_value.status_code = 404
    mock_get.return_value.json.return_value = {"error": "City not found"}
    
    result = get_weather("InvalidCity")
    
    # Check if the result indicates an error
    assert "error" in result
    assert result["error"] == "City 'InvalidCity' not found"


# Test Case 3: Test for API failure (e.g., network issues)
@patch('weather_service.requests.get')
def test_get_weather_api_failure(mock_get):
    # Mock an API failure (timeout)
    mock_get.side_effect = TimeoutError("Request timed out")
    
    # Check if the function handles the error properly
    with pytest.raises(TimeoutError):
        get_weather("London")