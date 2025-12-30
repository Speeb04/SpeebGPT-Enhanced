from __future__ import annotations
from dialogue.message import Message

class Conversation:
    """
    Conversation class to represent a list of messages.
    """

    _INSTRUCTIONS: str
    _MESSAGES: list[Message]
    _MAX_CONVERSATION_LENGTH = 15

    def __init__(self, instructions: str | None = None):
        if instructions is None:
            self._INSTRUCTIONS = """
            You are a helpful assistant named Speebot. 
            Give sassy and concise, but helpful responses. (Try and limit yourself to one or two sentences)
            Use the instructions given by the system to help form responses.
            """

        else:
            self._INSTRUCTIONS = instructions

        self._MESSAGES = [Message("system", self._INSTRUCTIONS)]

    def instructions(self) -> str | None:
        return self._INSTRUCTIONS

    def change_instructions(self, new_instructions: str) -> str:
        # Changes instructions to new ones and returns the old instructions
        self._INSTRUCTIONS = new_instructions
        return self._MESSAGES[0].change_text_content(new_instructions)

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
