from __future__ import annotations
from message import Message

class Conversation:
    """
    Conversation class to represent a list of messages.
    """

    _INSTRUCTIONS: str
    _MESSAGES: list[Message]

    def __init__(self, instructions: str | None):
        if instructions is None:
            self._INSTRUCTIONS = """You are a helpful assistant named Speebot. 
            Give sassy and concise, but helpful responses."""

        else:
            self._INSTRUCTIONS = instructions

    def add_message(self, message: Message) -> None:
        self._MESSAGES.append(message)

    def to_list_dict(self) -> list[dict]:
        output = []

        for message in self._MESSAGES:
            output.append(message.to_dict())

        return output
