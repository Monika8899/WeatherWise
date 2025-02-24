import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from typing import Dict, List, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not API_KEY:
    raise ValueError("OpenWeather API key not found in environment variables!")

# API endpoints
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

# Enhanced weather emojis and conditions mapping
WEATHER_EMOJIS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "fog": "🌫️",
    "haze": "🌫️",
    "dust": "😷",
    "smoke": "💨",
    "tornado": "🌪️",
    "default": "🌍"
}

# Weather recommendation mappings
WEATHER_RECOMMENDATIONS = {
    "clear": [
        "Perfect weather for outdoor activities! 🎾",
        "Don't forget your sunscreen! 🧴",
        "Great time for a picnic! 🧺",
        "Consider going for a hike! 🥾"
    ],
    "clouds": [
        "Good conditions for outdoor photography! 📸",
        "Nice weather for a walk! 🚶‍♂️",
        "Perfect for outdoor cafes! ☕",
        "Good day for sightseeing! 🏛️"
    ],
    "rain": [
        "Visit a museum or gallery! 🏛️",
        "Perfect for indoor shopping! 🛍️",
        "Catch up on reading! 📚",
        "Movie marathon weather! 🎬"
    ],
    "snow": [
        "Build a snowman! ⛄",
        "Go skiing or snowboarding! 🎿",
        "Perfect for hot chocolate! ☕",
        "Indoor board games day! 🎲"
    ]
}


def get_weather(city: str) -> Dict[str, Union[str, float]]:
    """
    Fetch detailed current weather data for a given city.

    Args:
        city (str): Name of the city

    Returns:
        dict: Weather data including temperature, humidity, wind speed, etc.
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        logger.info(f"Fetching weather data for {city}")
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract weather condition
        condition = data["weather"][0]["main"].lower()
        emoji = WEATHER_EMOJIS.get(condition, WEATHER_EMOJIS["default"])

        # Get weather recommendations
        recommendations = WEATHER_RECOMMENDATIONS.get(condition,
                                                      WEATHER_RECOMMENDATIONS.get(
                                                          "clear"))  # Default to clear weather recommendations

        # Process and format weather data
        weather_info = {
            "city": data["name"],
            "temperature": f"{round(data['main']['temp'], 1)}°C",
            "feels_like": f"{round(data['main']['feels_like'], 1)}°C",
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{round(data['wind']['speed'], 1)} m/s",
            "wind_direction": get_wind_direction(data['wind'].get('deg', 0)),
            "condition": f"{emoji} {data['weather'][0]['description'].capitalize()}",
            "pressure": f"{data['main']['pressure']} hPa",
            "visibility": f"{data['visibility'] / 1000:.1f} km",
            "sunrise": datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
            "sunset": datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
            "recommendations": recommendations,
            "raw_temp": data['main']['temp'],  # For calculations
            "raw_condition": condition  # For calculations
        }

        # Add air quality data if available
        air_quality = get_air_quality(data['coord']['lat'], data['coord']['lon'])
        if air_quality:
            weather_info.update(air_quality)

        logger.info(f"Successfully retrieved weather data for {city}")
        return weather_info

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data for {city}: {str(e)}")
        return {"error": f"Error fetching weather data: {str(e)}"}
    except (KeyError, ValueError) as e:
        logger.error(f"Error processing weather data for {city}: {str(e)}")
        return {"error": f"Error processing weather data: {str(e)}"}


def get_forecast(city: str, days: int = 7) -> List[Dict[str, str]]:
    """
    Fetch detailed weather forecast for specified number of days.

    Args:
        city (str): Name of the city
        days (int): Number of days for forecast (default 7)

    Returns:
        list: List of dictionaries containing forecast data
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "cnt": days * 8  # API returns data in 3-hour intervals
    }

    try:
        logger.info(f"Fetching {days}-day forecast for {city}")
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Process forecast data
        forecast = []
        daily_data = {}

        for item in data['list']:
            date = item['dt_txt'].split(' ')[0]

            if date not in daily_data:
                daily_data[date] = {
                    'temps': [],
                    'conditions': [],
                    'humidity': [],
                    'wind_speed': []
                }

            daily_data[date]['temps'].append(item['main']['temp'])
            daily_data[date]['conditions'].append(item['weather'][0]['main'].lower())
            daily_data[date]['humidity'].append(item['main']['humidity'])
            daily_data[date]['wind_speed'].append(item['wind']['speed'])

        # Calculate daily averages and most common condition
        for date, day_data in daily_data.items():
            avg_temp = sum(day_data['temps']) / len(day_data['temps'])
            most_common_condition = max(set(day_data['conditions']),
                                        key=day_data['conditions'].count)
            avg_humidity = sum(day_data['humidity']) / len(day_data['humidity'])
            avg_wind = sum(day_data['wind_speed']) / len(day_data['wind_speed'])

            emoji = WEATHER_EMOJIS.get(most_common_condition, WEATHER_EMOJIS["default"])

            forecast.append({
                "date": format_date(date),
                "temperature": f"{round(avg_temp, 1)}°C",
                "condition": f"{emoji} {most_common_condition.capitalize()}",
                "humidity": f"{round(avg_humidity)}%",
                "wind_speed": f"{round(avg_wind, 1)} m/s",
                "recommendations": WEATHER_RECOMMENDATIONS.get(
                    most_common_condition,
                    WEATHER_RECOMMENDATIONS["clear"]
                )[0]  # Get first recommendation
            })

        logger.info(f"Successfully retrieved forecast data for {city}")
        return forecast

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching forecast for {city}: {str(e)}")
        return {"error": f"Error fetching forecast data: {str(e)}"}
    except (KeyError, ValueError) as e:
        logger.error(f"Error processing forecast for {city}: {str(e)}")
        return {"error": f"Error processing forecast data: {str(e)}"}


def get_air_quality(lat: float, lon: float) -> Dict[str, str]:
    """
    Fetch air quality data for given coordinates.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Air quality data
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    try:
        response = requests.get(AIR_QUALITY_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        aqi = data['list'][0]['main']['aqi']
        aqi_labels = {
            1: "Good 😊",
            2: "Fair 🙂",
            3: "Moderate 😐",
            4: "Poor 😷",
            5: "Very Poor 🤢"
        }

        return {
            "air_quality": aqi_labels.get(aqi, "Unknown"),
            "air_quality_index": aqi
        }
    except:
        logger.warning("Could not fetch air quality data")
        return {}


def get_wind_direction(degrees: float) -> str:
    """
    Convert wind degrees to cardinal direction.

    Args:
        degrees (float): Wind direction in degrees

    Returns:
        str: Cardinal direction
    """
    directions = [
        "North", "North-Northeast", "Northeast", "East-Northeast",
        "East", "East-Southeast", "Southeast", "South-Southeast",
        "South", "South-Southwest", "Southwest", "West-Southwest",
        "West", "West-Northwest", "Northwest", "North-Northwest"
    ]
    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]


def format_date(date_str: str) -> str:
    """
    Format date string to more readable format.

    Args:
        date_str (str): Date string in YYYY-MM-DD format

    Returns:
        str: Formatted date string
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%A, %B %d')  # e.g., "Monday, January 15"


def calculate_feels_like(temperature: float, humidity: float, wind_speed: float) -> float:
    """
    Calculate "feels like" temperature using weather parameters.

    Args:
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage
        wind_speed (float): Wind speed in m/s

    Returns:
        float: Feels like temperature in Celsius
    """
    # Simple heat index calculation for warm temperatures
    if temperature > 27:
        feels_like = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + (humidity * 0.094))
        return (feels_like - 32) * 5 / 9  # Convert to Celsius

    # Wind chill calculation for cold temperatures
    elif temperature < 10:
        wind_kph = wind_speed * 3.6  # Convert m/s to km/h
        feels_like = (13.12 + 0.6215 * temperature -
                      11.37 * (wind_kph ** 0.16) +
                      0.3965 * temperature * (wind_kph ** 0.16))
        return feels_like

    # Return actual temperature if between 10-27°C (no adjustment needed)
    return temperature

# Example usage
if __name__ == "__main__":
    # Test the weather service
    test_city = "London"
    weather = get_weather(test_city)
    if "error" not in weather:
        print(f"\nCurrent weather in {test_city}:")
        for key, value in weather.items():
            if key not in ['recommendations', 'raw_temp', 'raw_condition']:
                print(f"{key}: {value}")

    forecast = get_forecast(test_city)
    if isinstance(forecast, list):
        print(f"\nForecast for {test_city}:")
        for day in forecast:
            print(f"\n{day['date']}:")
            print(f"Temperature: {day['temperature']}")
            print(f"Condition: {day['condition']}")
            print(f"Recommendation: {day['recommendations']}")
def get_weather(city):
    """Fetch weather data from OpenWeatherMap API."""
    if not API_KEY:
        return {"error": "API key not configured"}
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 404:
            return {"error": f"City '{city}' not found"}
        elif response.status_code == 401:
            return {"error": "Invalid API key"}
        
        response.raise_for_status()
        data = response.json()
        
        return {
            "city": data.get("name", "Unknown City"),
            "temperature": f"{data['main']['temp']}°C",
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
            "condition": data['weather'][0]['description'].capitalize()
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching weather data: {str(e)}"}