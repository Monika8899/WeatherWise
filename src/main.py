import os
from dotenv import load_dotenv
from city_storage import add_city, load_cities
from weather_api import get_weather

load_dotenv()  # Load environment variables

def display_weather(city):
    """Display the weather information for a given city."""
    weather_data = get_weather(city)
    if weather_data:
        print(f"Weather in {city}:")
        print(f"Temperature: {weather_data['main']['temp']}K")
        print(f"Weather: {weather_data['weather'][0]['description']}")
        print(f"Humidity: {weather_data['main']['humidity']}%")
    else:
        print(f"Could not retrieve weather data for {city}.")

def main():
    while True:
        print("\nWeather App")
        print("1. Add a city")
        print("2. View cities")
        print("3. Get weather for a city")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            city_name = input("Enter the city name: ")
            add_city(city_name)
            print(f"City {city_name} added.")
        elif choice == "2":
            cities = load_cities()
            print("Cities in your list:")
            for city in cities:
                print(city)
        elif choice == "3":
            city_name = input("Enter the city name to get weather: ")
            display_weather(city_name)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
