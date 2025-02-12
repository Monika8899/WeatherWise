import requests
import os

def get_weather(city):
    """Fetch weather data for the given city."""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
