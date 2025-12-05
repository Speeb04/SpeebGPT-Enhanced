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
    def weather_lookup(location: str, units: str = 'metric') -> dict:

        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q="
                                f"{location}&appid={WeatherAPIGateway._WEATHER_API_KEY}&units={units}")

        if response.status_code != 200:
            raise IOError(f"Error retrieving weather data: {response.status_code}")

        response_json = response.json()

        # Get current local time
        local_now = datetime.now()

        # Get current UTC time
        utc_now = datetime.now(timezone.utc)

        # Calculate the difference
        offset_timedelta = local_now - utc_now

        sunrise_time = datetime.fromtimestamp(response['sys']['sunrise'] + response['timezone'] + offset_timedelta.total_seconds())
        sunrise_time = sunrise_time.strftime('%I:%M %p').lstrip('0')

        sunset_time = datetime.fromtimestamp(response['sys']['sunset'] + response['timezone'] + 25200)
        sunset_time = sunset_time.strftime('%I:%M %p').lstrip('0')

        return {
            # Location data
            "city": response_json["name"],
            "country": response_json["sys"]["country"],

            # Weather description
            "description": response_json["weather"][0]["description"],

            # Temperature info
            "temp_max": response_json['main']['temp_max'],
            "temp_min": response_json['main']['temp_min'],
            "feels_like": response_json['main']['feels_like'],

            # Sunrise/Sunset
            "sunrise_time": sunrise_time,
            "sunset_time": sunset_time,
        }
