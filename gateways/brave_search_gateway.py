from __future__ import annotations

import requests
import os

from gateways.singleton import Singleton


class BraveSearchGateway(metaclass=Singleton):
    """A gateway to access the Brave Search API."""

    _BRAVE_SEARCH_API_KEY: str = os.environ.get("BRAVE_SEARCH_API_KEY")
    _DEFAULT_GET_URL: str = "https://api.search.brave.com/res/v1/web/search"

    country: str

    def __init__(self, country: str = None) -> None:
        if country is None:
            self.country = "CA"
        else:
            self.country = country

    def _search(self, query: str) -> list[dict]:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "x-subscription-token": BraveSearchGateway._BRAVE_SEARCH_API_KEY,
            },
            params={
                "q": query,
                "country": self.country,
                "safesearch": "strict",
                "count": 3
            },
        ).json()

        import pprint
        pprint.pprint(response)

        if len(response["web"]["results"]) > 3:
            return response["web"]["results"][:3]

        return response["web"]["results"]

    def concise_search(self, query: str) -> list[dict]:
        """Same as _search, but removes extra metadata from responses to reduce fluff."""
        response = self._search(query)
        concise_responses = []
        for result in response:
            concise_responses.append({
                "title": result["title"],
                "url": result["url"],
                "description": result["description"],
                "hostname": result["meta_url"]["netloc"]
            })

        return concise_responses
