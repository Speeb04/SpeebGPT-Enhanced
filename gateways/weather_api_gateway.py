from __future__ import annotations

from datetime import datetime
from datetime import timezone
import requests
import os

from gateways.singleton import Singleton


class WeatherAPIGateway(metaclass=Singleton):
    """Gateway to access the OpenWeatherMap API."""

    _WEATHER_API_KEY: str = os.environ['WEATHER_API_KEY']
    
    @staticmethod
    def get_wind_direction(deg: float) -> str:
        if 22.5 < deg <= 67.5:
            wind_direction = "Northeast"

        elif 67.5 < deg <= 112.5:
            wind_direction = "East"

        elif 112.5 < deg <= 157.5:
            wind_direction = "Southeast"

        elif 157.5 < deg <= 202.5:
            wind_direction = "South"

        elif 202.5 < deg <= 247.5:
            wind_direction = "Southwest"

        elif 247.5 < deg <= 292.5:
            wind_direction = "West"

        elif 292.5 < deg <= 337.5:
            wind_direction = "Northwest"

        else:
            wind_direction = "North"

        return wind_direction

    def weather_lookup(self, location: str, units: str = 'metric') -> dict:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q="
                                f"{location}&appid={WeatherAPIGateway._WEATHER_API_KEY}&units={units}")

        if response.status_code != 200:
            raise IOError(f"Error retrieving weather data: {response.status_code}")

        response_json = response.json()

        # Get current local time
        local_now = datetime.now().hour

        # Get current UTC time
        utc_now = datetime.now(timezone.utc).hour

        sunrise_time = datetime.fromtimestamp(response_json['sys']['sunrise'] + response_json['timezone'] + 5 * 3600)
        sunrise_time = sunrise_time.strftime('%I:%M %p').lstrip('0')

        sunset_time = datetime.fromtimestamp(response_json['sys']['sunset'] + response_json['timezone'] + 5 * 3600)
        sunset_time = sunset_time.strftime('%I:%M %p').lstrip('0')
        
        if response_json['visibility'] < 10000:
            visibility = f"{response_json['visibility'] / 1000} km"
        else:
            visibility = "good visibility"

        wind_direction = WeatherAPIGateway.get_wind_direction(response_json['wind']['deg'])
        wind_speed = round(response_json['wind']['speed'] * (3.6 if units == "metric" else 1))

        if "rain" in response_json:
            rain = response_json['rain']['1h']
        else:
            rain = 0

        if "snow" in response_json:
            snow = response_json['snow']['1h']
        else:
            snow = 0

        return {
            # Location data
            "city": response_json["name"],
            "country": response_json["sys"]["country"],

            # Weather description
            "description": response_json["weather"][0]["description"],

            # Temperature info
            "temp": response_json["main"]["temp"],
            "temp_max": response_json['main']['temp_max'],
            "temp_min": response_json['main']['temp_min'],
            "feels_like": response_json['main']['feels_like'],

            # Sunrise/Sunset
            "sunrise_time": sunrise_time,
            "sunset_time": sunset_time,

            # Visibility and wind
            "visibility": visibility,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,

            # Rain and snow
            "rain": rain,
            "snow": snow,

            # Icon
            "icon": response_json['weather'][0]['icon'],
        }
