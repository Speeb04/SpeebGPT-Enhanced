from __future__ import annotations
import base64
from typing import final


@final
class Message:
    """
    Message object for conversation, to use for OpenAI API integration.
    """

    # Images and files attachments
    images: list[Image] | None
    files: list[File] | None
    text_content: str

    def __init__(self, role: str, text_content: str,
                 images: list[Image] = None, files: list[File] = None):
        self.role = role
        self.text_content = text_content

        self.images = images
        self.files = files

        # allows for empty lists to be initialized as NoneType
        if isinstance(images, list):
            if len(images) == 0:
                self.images = None

        if isinstance(files, list):
            if len(files) == 0:
                self.files = None

    def has_images(self):
        return self.images is not None

    def has_files(self):
        return self.files is not None

    # THIS METHOD SHOULD ONLY BE USED FOR CHANGING THE INSTRUCTIONS
    def change_text_content(self, new_content: str) -> str:
        # returns the previous text content
        old_content = self.text_content
        self.text_content = new_content

        return old_content

    # helper functions for to_dict
    def _files_to_dict_list(self) -> list[dict]:

        # Ensure that message has file attachments
        if not self.has_files():
            raise AttributeError("Message has no files")

        output = []
        for file in self.files:
            output.append({
                "type": "file",
                "file": {
                    "filename": file.filename,
                    "file_data": f"data:application/pdf;base64,{file.b64_file}"
                }
            })

        return output

    def _images_to_dict_list(self) -> list[dict]:
        if not self.has_images():
            raise AttributeError("Message has no images")

        output = []
        for image in self.images:
            output.append({
                "type": "image_url",
                # "image_data": f"data:image/{image.type};base64,{image.b64_image}"
                "image_url": {
                    "url": image.url
                }
            })

        return output

    def to_dict(self) -> dict:
        content_list = []

        if self.has_images():
            content_list.extend(self._images_to_dict_list())

        if self.has_files():
            content_list.extend(self._files_to_dict_list())

        content_list.append({
            "type": "text",
            "text": self.text_content
        })

        return {"role": self.role, "content": content_list}


@final
class Image:
    """
    Creates an image object from a bytes object, encoded in base64 to
    use with the OpenAI API.
    """

    # base64 encoded image in UTF-8 format
    # b64_image: str
    # type: str

    def __init__(self, url: str) -> None:
        # self.b64_image = base64.b64encode(image_bytes).decode("utf-8")
        # self.type = type
        self.url = url


@final
class File:
    """
    Creates a file object from a bytes object, encoded in base64 to
    use with the OpenAI API.

    Note: the API only supports PDF files, so by default all files are
    explicitly treated as PDF files.
    """

    filename: str

    # base64 encoded file in UTF-8 format
    b64_file: str

    def __init__(self, filename: str, file_bytes: bytes) -> None:
        self.filename = filename
        self.b64_file = base64.b64encode(file_bytes).decode("utf-8")
