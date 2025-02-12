import requests

class WeatherFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        """Fetches current weather data for a given city using OpenWeatherMap API."""
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "imperial"  
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            if response.ok:
                data = response.json()

                if "main" in data and "weather" in data:
                    return {
                        "city": data.get("name", "Unknown City"),
                        "temperature": data["main"].get("temp", "N/A"),
                        "humidity": data["main"].get("humidity", "N/A"),
                        "weather": data["weather"][0].get("description", "N/A")
                    }
                else:
                    return {"error": "Invalid response structure from API."}

        except requests.exceptions.HTTPError as http_err:
            return {"error": f"HTTP error: {http_err}"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Please check your internet connection."}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Try again later."}
        except requests.exceptions.RequestException as req_err:
            return {"error": f"API request error: {req_err}"}
        except KeyError as key_err:
            return {"error": f"Unexpected data structure in response: {key_err}"}

# Example
if __name__ == "__main__":
    API_KEY = "067d8918137138efbb6c1584556bab8d"  
    city = input("Enter city name: ").strip()  
    weather_fetcher = WeatherFetcher(API_KEY)
    weather_data = weather_fetcher.get_weather(city)
    
    if "error" in weather_data:
        print(f"Error: {weather_data['error']}")
    else:
        print("\nWeather Information:")
        print(f"City: {weather_data['city']}")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Weather: {weather_data['weather'].capitalize()}")