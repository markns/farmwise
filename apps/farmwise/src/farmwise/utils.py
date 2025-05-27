from __future__ import annotations

import base64
from pathlib import Path

from farmwise.service import client


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


def image_to_data_url(file_path: str) -> str:
    """Convert a JPEG file to a base64-encoded data URL."""
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type = "image/jpeg"  # You can make this dynamic if needed

    with file.open("rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"


def create_openai_file(file_path):
    # This is more useful than sending base64, as it means the base64 does not get
    # sent back and forth repeatedly
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id
