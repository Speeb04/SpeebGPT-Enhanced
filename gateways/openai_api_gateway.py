from __future__ import annotations
from google import genai

from singleton import Singleton
import os

class GoogleAPIGateway(metaclass=Singleton):
    """
    Each project should only implement at most one API Gateway.
    This is to avoid abuse and rate limiting.
    """
    # private static variable: Google Genai API key
    _GENAI_TOKEN = os.environ["GENAI_TOKEN"]
    _MODEL: str

    def __init__(self, model: str = "gemini-3-pro-preview"):
        self._MODEL = model

    @property
    def model(self) -> str:
        return self._MODEL

    @model.setter
    def model(self, model: str) -> None:
        self._MODEL = model

    



