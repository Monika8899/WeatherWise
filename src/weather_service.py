import requests
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Emoji representations of weather conditions
WEATHER_EMOJIS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}

def get_weather(city):
    """Fetch current weather data from OpenWeatherMap API."""
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        condition = data["weather"][0]["main"].lower()
        return {
            "city": data["name"],
            "temperature": f"{data['main']['temp']}°C",
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
            "condition": f"{WEATHER_EMOJIS.get(condition, '🌍')} {data['weather'][0]['description'].capitalize()}"
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching weather data: {e}"}

def get_forecast(city):
    """Fetch 7-day weather forecast."""
    params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": 7}
    try:
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()
        forecast = []
        for day in data['list']:
            condition = day['weather'][0]['main'].lower()
            forecast.append({
                "date": day["dt_txt"].split(" ")[0],
                "temperature": f"{day['main']['temp']}°C",
                "condition": f"{WEATHER_EMOJIS.get(condition, '🌍')} {day['weather'][0]['description'].capitalize()}"
            })
        return forecast
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching forecast data: {e}"}
