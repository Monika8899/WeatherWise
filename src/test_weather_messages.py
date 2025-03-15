import unittest
from unittest.mock import patch
import random

# Functions to test (normally imported, included here for completeness)
def get_rotating_message(message_list, seed=None):
    """Get a random message with optional seed for testing."""
    if seed is not None:
        random.seed(seed)
    return random.choice(message_list)

def generate_fun_forecast_message(forecast_data, message_collections=None):
    """Generate weather-appropriate messages for forecast days."""
    if message_collections is None:
        message_collections = {
            'rain': ["🌧️ Rain message 1", "🌧️ Rain message 2"],
            'snow': ["❄️ Snow message 1", "❄️ Snow message 2"],
            'clear_hot': ["☀️ Hot message 1", "☀️ Hot message 2"],
            'clear_mild': ["🌤️ Mild message 1", "🌤️ Mild message 2"],
            'cloudy': ["☁️ Cloudy message 1", "☁️ Cloudy message 2"],
            'default': ["🌈 Default message"]
        }
    
    messages = []
    for day in forecast_data:
        condition = day['condition'].lower()
        temp = float(day['temperature'].replace('°C', ''))
        date = day['date']

        if 'rain' in condition:
            message = get_rotating_message(message_collections['rain'])
        elif 'snow' in condition:
            message = get_rotating_message(message_collections['snow'])
        elif 'clear' in condition and temp > 25:
            message = get_rotating_message(message_collections['clear_hot'])
        elif 'clear' in condition and temp <= 25:
            message = get_rotating_message(message_collections['clear_mild'])
        elif 'cloud' in condition:
            message = get_rotating_message(message_collections['cloudy'])
        else:
            message = get_rotating_message(message_collections['default'])

        messages.append(f"{date}: {message}")
    return messages

class TestWeatherMessages(unittest.TestCase):
    """Test class for weather message functions."""
    
    def setUp(self):
        """Set up test data."""
        self.test_messages = {k: [f"TEST {k.upper()} MESSAGE"] for k in 
                             ['rain', 'snow', 'clear_hot', 'clear_mild', 'cloudy', 'default']}
        self.test_cases = [
            {'date': '2025-02-25', 'temp': '15°C', 'condition': 'Light rain', 'expected': 'rain'},
            {'date': '2025-02-25', 'temp': '0°C', 'condition': 'Heavy snow', 'expected': 'snow'},
            {'date': '2025-02-25', 'temp': '30°C', 'condition': 'Clear sky', 'expected': 'clear_hot'},
            {'date': '2025-02-25', 'temp': '20°C', 'condition': 'Clear sky', 'expected': 'clear_mild'},
            {'date': '2025-02-25', 'temp': '18°C', 'condition': 'Partly cloudy', 'expected': 'cloudy'},
            {'date': '2025-02-25', 'temp': '18°C', 'condition': 'Unusual', 'expected': 'default'}
        ]
    
    def test_weather_conditions(self):
        """Test all weather condition branches."""
        for case in self.test_cases:
            forecast = [{'date': case['date'], 'temperature': case['temp'], 'condition': case['condition']}]
            messages = generate_fun_forecast_message(forecast, self.test_messages)
            self.assertEqual(messages[0], f"{case['date']}: TEST {case['expected'].upper()} MESSAGE")
    
    def test_multiple_days(self):
        """Test multiple forecast days."""
        multi_forecast = [{'date': case['date'], 'temperature': case['temp'], 
                          'condition': case['condition']} for case in self.test_cases[:3]]
        messages = generate_fun_forecast_message(multi_forecast, self.test_messages)
        self.assertEqual(len(messages), 3)
        for i, case in enumerate(self.test_cases[:3]):
            self.assertEqual(messages[i], f"{case['date']}: TEST {case['expected'].upper()} MESSAGE")

if __name__ == '__main__':
    unittest.main()