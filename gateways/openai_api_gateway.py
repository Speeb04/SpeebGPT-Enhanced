from __future__ import annotations
from openai import OpenAI

from gateways.singleton import Singleton


# NOTE: The API key is retrieved from the environment variable `OPENAI_API_KEY`.
class OpenAIGateway(metaclass=Singleton):
    """
    Each project should only implement at most one API Gateway.
    This is to avoid abuse and rate limiting.
    """
    # private static variable: Google Genai API key
    _MODEL: str
    _REASONING: str

    def __init__(self, model: str = "gpt-5-nano", reasoning: str = "low"):
        self._MODEL = model
        self._REASONING = reasoning
        self.client = OpenAI()

    @property
    def model(self) -> str:
        return self._MODEL

    @model.setter
    def model(self, model: str) -> None:
        self._MODEL = model

    def generate_response(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self._MODEL,
            messages=messages
        )

        return response.choices[0].message.content

    def moderation_filter(self, message: str) -> bool:
        # returns True if the content is explicit.
        response = self.client.moderations.create(
            model="omni-moderation-latest",
            input=message,
        ).to_dict()

        return response['results'][0]['flagged']
