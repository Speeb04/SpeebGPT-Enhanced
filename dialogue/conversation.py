from __future__ import annotations
from dialogue.message import Message

class Conversation:
    """
    Conversation class to represent a list of messages.
    """

    _INSTRUCTIONS: str
    _MESSAGES: list[Message]
    _MAX_CONVERSATION_LENGTH = 10

    def __init__(self, instructions: str | None = None):
        if instructions is None:
            self._INSTRUCTIONS = """
            You are a helpful assistant named Speebot. 
            Give sassy and concise, but helpful responses. (In particular, at most around 70 words)
            Use the search results given by the system to help form responses.
            """

        else:
            self._INSTRUCTIONS = instructions

        self._MESSAGES = [Message("system", self._INSTRUCTIONS)]

    @property
    def instructions(self) -> str | None:
        return self._INSTRUCTIONS

    def add_message(self, message: Message) -> None:
        self._MESSAGES.append(message)
        self.ensure_length()

    def to_list_dict(self) -> list[dict]:
        output = []

        for message in self._MESSAGES:
            output.append(message.to_dict())

        return output

    def ensure_length(self):
        while len(self._MESSAGES) > self._MAX_CONVERSATION_LENGTH:
            self._MESSAGES.pop(1)
