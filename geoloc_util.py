# geoloc_util.py
import argparse
import requests
import sys
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load API key from environment variables
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "http://api.openweathermap.org/geo/1.0"

def get_location_by_city_state(location: str) -> Dict:
    """Get coordinates for a city,state combination."""
    city, state = [x.strip() for x in location.split(',')]
    
    params = {
        'q': f"{city},{state},US",
        'limit': 1,
        'appid': API_KEY
    }
    
    response = requests.get(f"{BASE_URL}/direct", params=params)
    response.raise_for_status()
    
    results = response.json()
    if not results:
        raise ValueError(f"No results found for {location}")
    
    return {
        'name': results[0]['name'],
        'state': results[0]['state'],
        'country': results[0]['country'],
        'lat': results[0]['lat'],
        'lon': results[0]['lon']
    }

def get_location_by_zipcode(zipcode: str) -> Dict:
    """Get coordinates for a zipcode."""
    params = {
        'zip': f"{zipcode},US",
        'appid': API_KEY
    }
    
    try:
        response = requests.get(f"{BASE_URL}/zip", params=params)
        response.raise_for_status()
        result = response.json()
        if 'cod' in result and result['cod'] != 200:
            raise ValueError(f"No results found for zipcode {zipcode}")
    except requests.exceptions.HTTPError:
        raise ValueError(f"Invalid zipcode format or not found: {zipcode}")
    
    return {
        'name': result['name'],
        'country': result['country'],
        'lat': result['lat'],
        'lon': result['lon'],
        'zip': zipcode
    }

def process_location(location: str) -> Dict:
    """Process a single location, determining if it's a zipcode or city,state."""
    if not location or not location.strip():
        raise ValueError("Location cannot be empty")
        
    try:
        if ',' in location:
            return get_location_by_city_state(location)
        else:
            return get_location_by_zipcode(location)
    except Exception as e:
        print(f"Error processing location '{location}': {str(e)}")
        return None

def main(locations: List[str]) -> None:
    """Main function to process multiple locations."""
    for location in locations:
        result = process_location(location)
        if result:
            print(f"\nLocation Information for: {location}")
            print("-" * 40)
            for key, value in result.items():
                print(f"{key.capitalize()}: {value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get geolocation information for US locations')
    parser.add_argument('locations', nargs='+', help='List of locations (city,state or zipcode)')
    args = parser.parse_args()
    main(args.locations)