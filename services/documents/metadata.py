import mimetypes
from typing import Any


def document_name(name: Any) -> str | None:
    if isinstance(name, str):
        return name

    if isinstance(name, dict):
        for value in name.values():
            if isinstance(value, str):
                return value

    return None


def document_mime_type(document: Any, name: str | None) -> str | None:
    mime_type = getattr(document, "mime_type", None)
    if mime_type:
        return mime_type

    guessed, _ = mimetypes.guess_type(name or "")
    return guessed


def document_caption(document: Any) -> str | None:
    caption = getattr(document, "caption", None)
    if caption is None:
        return None

    return getattr(caption, "content", None)
