import os

import requests
from bs4 import BeautifulSoup as BS


def get_weather_from_sinoptik(city):
    response = requests.get(
        f"https://sinoptik.ua/погода-{city}")
    return BS(response.content, 'html.parser') if response.status_code == 200 else False


def get_weather_from_ow(coords):
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/onecall", {'lat': int(coords['lat']), 'lon': int(coords['lng']),
                                                            'exclude': 'current,minutely,hourly,alerts',
                                                            'units': 'metric', 'appid': os.environ['API_KEY_OW'],
                                                            'lang': 'ru'})
    return response.json() if response.status_code == 200 else False


def get_city_info(city):
    response = requests.get(
        "https://api.opencagedata.com/geocode/v1/json",
        {'key': os.environ['API_KEY_OPEN_CAGE'], 'q': city, 'language': 'ru'})
    if response.status_code == 200:
        data = response.json()
        results = data['results'][0]
        components = results['components']
        if 'city' in components.keys():
            location_name = components['city']
        elif 'town' in components.keys():
            location_name = components['town']
        elif 'county' in components.keys():
            location_name = components['county']
        else:
            location_name = components['state']
        return {
            'location_name': location_name,
            'coords': results['geometry']
        }
    return False
