from __future__ import annotations
from openai import OpenAI

from singleton import Singleton
import os


# NOTE: The API key is retrieved from the environment variable `OPENAI_API_KEY`.
class OpenAIGateway(metaclass=Singleton):
    """
    Each project should only implement at most one API Gateway.
    This is to avoid abuse and rate limiting.
    """
    # private static variable: Google Genai API key
    _OPENAI_TOKEN = os.environ["GENAI_TOKEN"]
    _MODEL: str
    _REASONING: str

    def __init__(self, model: str = "gpt-5", reasoning: str = "medium"):
        self._MODEL = model
        self._REASONING = reasoning
        self.client = OpenAI()

    @property
    def model(self) -> str:
        return self._MODEL

    @model.setter
    def model(self, model: str) -> None:
        self._MODEL = model

    def generate_response(self, instructions: str, messages: list) -> str:
        response = self.client.responses.create(
            model=self._MODEL,
            instructions=instructions,
            input=messages
        )

        return response.output_text
