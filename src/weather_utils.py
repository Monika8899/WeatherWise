import pytest
from app import get_weather_alerts
from unittest.mock import patch


# Test when there is an unusually high temperature
@patch('app.get_temperature_trends')
def test_high_temperature_alert(mock_get_trends):
    # Mock the database function to return historical data
    mock_get_trends.return_value = [(0, 0, 20.0, 0, 'clear')]  # 20°C average

    # Call the function with temperature significantly higher than average
    alerts = get_weather_alerts('TestCity', 26.0, 'clear', {})

    # Check if high temperature alert is in the results
    assert any("unusually high" in alert for alert in alerts)


# Test when there is an unusually low temperature
@patch('app.get_temperature_trends')
def test_low_temperature_alert(mock_get_trends):
    # Mock the database function to return historical data
    mock_get_trends.return_value = [(0, 0, 20.0, 0, 'clear')]  # 20°C average

    # Call the function with temperature significantly lower than average
    alerts = get_weather_alerts('TestCity', 14.0, 'clear', {})

    # Check if low temperature alert is in the results
    assert any("unusually low" in alert for alert in alerts)


# Test for severe weather conditions
def test_severe_weather_alert():
    # Call function with a severe weather condition
    alerts = get_weather_alerts('TestCity', 20.0, 'thunderstorm', {})

    # Check if severe weather alert is in the results
    assert any("SEVERE WEATHER ALERT" in alert for alert in alerts)


# Test when air quality is poor
def test_air_quality_alert():
    # Test with poor air quality data
    weather_data = {'air_quality_index': 5}
    alerts = get_weather_alerts('TestCity', 20.0, 'clear', weather_data)

    # Check if air quality alert is in results
    assert any("AIR QUALITY ALERT" in alert for alert in alerts)