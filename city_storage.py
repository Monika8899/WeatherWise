import json

def load_cities():
    """Load cities from the JSON file."""
    try:
        with open('cities.json', 'r') as file:
            data = json.load(file)
        return data.get('cities', [])
    except FileNotFoundError:
        return []

def save_cities(cities):
    """Save cities to the JSON file."""
    with open('cities.json', 'w') as file:
        json.dump({"cities": cities}, file, indent=4)

def add_city(city_name):
    """Add a city to the list of cities."""
    cities = load_cities()
    if city_name not in cities:
        cities.append(city_name)
        save_cities(cities)
    else:
        print(f"{city_name} is already in your list of cities.")
