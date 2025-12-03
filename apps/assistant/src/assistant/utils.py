from __future__ import annotations

import base64
from pathlib import Path

from google.genai import types

def image_to_base64(file_path: Path | str) -> str:
    """Read an image file and return its base64-encoded string."""
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with file.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def copy_doc(from_func):
    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__
        return to_func

    return decorator


def join_with(words, join_word="or"):
    if not words:
        return ""
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        return f" {join_word} ".join(words)
    return ", ".join(words[:-1]) + f" {join_word} " + words[-1]


def image_to_data_url(file_path: str) -> types.Part:
    """Convert an image file to a Google GenAI Part object."""
    mime_type = "image/jpeg"  # You can make this dynamic if needed
    with open(file_path, "rb") as image_file:
        image_bytes = image_file.read()
    return types.Part.from_data(data=image_bytes, mime_type=mime_type)

def to_adk_content(user_input: "UserInput") -> list[types.Part]:
    content_parts = []
    if user_input.text:
        content_parts.append(types.Part.from_text(user_input.text))
    if user_input.image:
        # Assuming user_input.image is a local file path
        # If it's a URL, you'd need to fetch it first
        try:
            content_parts.append(image_to_data_url(user_input.image))
        except FileNotFoundError:
            # Handle case where image file might not exist
            pass
    return content_parts
