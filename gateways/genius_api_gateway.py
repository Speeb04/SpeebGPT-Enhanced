from __future__ import annotations

import os

from lyricsgenius import Genius

from gateways.singleton import Singleton


class GeniusAPIGateway(metaclass=Singleton):
    """Genius API Gateway, using the lyricsgenius library (because I was too
    lazy to implement the http requests myself."""

    _GENIUS_API_KEY = os.environ.get("GENIUS_API_KEY")
    genius: Genius

    def __init__(self):
        self.genius = Genius(self._GENIUS_API_KEY)

        # Turns off the printed outputs.
        self.genius.verbose = False

    def get_song_info(self, song: str, artist: str) -> dict:
        try:
            song_id = self.genius.search(f"{song} {artist}")['hits'][0]['result']['id']
        except Exception:
            raise IOError(f"Could not find song {song} by {artist}")

        song_info = self.genius.song(song_id)['song']

        return {
            "title": song_info["full_title"],
            "description": song_info["description"]["plain"],
            "lyrics": self.genius.lyrics(song_id, remove_section_headers=True),
            "artists": song_info["artist_names"],
            "album": song_info["album"]["name"],
            "release_date": song_info["release_date_for_display"],
            "url": song_info["url"],
            "icon_url": song_info['album']['cover_art_url']
        }

    def get_artist_info(self, artist: str) -> dict:
        try:
            artist_id = self.genius.search_artist(artist, max_songs=0).id
            artist_info = self.genius.artist(artist_id)['artist']
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
