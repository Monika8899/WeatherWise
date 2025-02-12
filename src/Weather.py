import requests
import os
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather(city):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        print(f"City: {data['name']}")
        print(f"Temperature: {data['main']['temp']}°C")
        print(f"Humidity: {data['main']['humidity']}%")
        print(f"Wind Speed: {data['wind']['speed']} m/s")
        print(f"Condition: {data['weather'][0]['description'].capitalize()}")

    except requests.exceptions.HTTPError:
        print(f"Oops! '{city}' is not a real city. Try again!")
    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == "__main__":
    city_name = input("Enter city name: ")
    get_weather(city_name)
