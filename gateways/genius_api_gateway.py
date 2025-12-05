from __future__ import annotations

import requests
import os

from gateways.singleton import Singleton


class GeniusAPIGateway(metaclass=Singleton):
    """Genius API Gateway, using the lyricsgenius library (because I was too
    lazy to implement the http requests myself."""

    _GENIUS_API_KEY = os.environ.get("GENIUS_API_KEY")

    def get_song_info(self, song: str, artist: str) -> dict:
        try:
            response = requests.get(f"https://api.genius.com/search?q={song}&access_token={self._GENIUS_API_KEY}")
            song_id = response.json()['response']['hits'][0]['result']['id']
        except Exception:
            raise IOError(f"Could not find song {song} by {artist}")

        song_info = requests.get(f"https://api.genius.com/songs/{song_id}?"
                                 f"text_format=plain&access_token={self._GENIUS_API_KEY}").json()['response']['song']

        return {
            "title": song_info["full_title"],
            "description": song_info["description"]["plain"],
            "artists": song_info["artist_names"],
            "album": song_info["album"]["name"],
            "release_date": song_info["release_date_for_display"],
            "url": song_info["url"],
            "icon_url": song_info['album']['cover_art_url']
        }

    def get_artist_info(self, artist: str) -> dict:
        try:
            # This will probably return a song.
            song = requests.get(f"https://api.genius.com/search?q={artist}&access_token={self._GENIUS_API_KEY}").json()
            artist_id = song['response']['hits'][0]['result']['primary_artist']['id']
            artist_info = requests.get(f"https://api.genius.com/songs/{artist_id}?"
                                     f"text_format=plain&access_token={self._GENIUS_API_KEY}").json()['response']['artist']
        except Exception as e:
            print(e)
            raise IOError(f"Could not find artist {artist}")

        return {
            "name": artist_info["name"],
            "description": artist_info["description"]["plain"],
            "alternate_names": ', '.join(artist_info["alternate_names"]),
            "icon_url": artist_info["image_url"],
            "url": artist_info["url"],

            # Social media
            "instagram": artist_info["instagram_name"],
            "twitter": artist_info["twitter_name"]
        }

