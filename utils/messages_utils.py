import io
import mimetypes
from typing import Any

from aiobale import Client
from aiobale.types import Message


MAX_INLINE_FILE_BYTES = 1_000_000
MAX_INLINE_TEXT_CHARS = 200_000

def get_chat_type_value(chat_type) -> int:
    """
    Convert chat type to int safely.
    It supports both raw int and Enum-like values.
    """
    if hasattr(chat_type, "value"):
        return int(chat_type.value)

    return int(chat_type)

def _document_name(name: Any) -> str | None:
    if isinstance(name, str):
        return name

    if isinstance(name, dict):
        for value in name.values():
            if isinstance(value, str):
                return value

    return None


def _document_mime_type(document) -> str:
    mime_type = getattr(document, "mime_type", None)
    if mime_type:
        return mime_type

    guessed, _ = mimetypes.guess_type(_document_name(document.name) or "")
    return guessed or "application/octet-stream"


def _is_text_document(name: str | None, mime_type: str) -> bool:
    if mime_type.startswith("text/"):
        return True

    if mime_type in {
        "application/json",
        "application/xml",
        "application/javascript",
        "application/x-python-code",
        "application/x-sh",
    }:
        return True

    if name:
        return name.lower().endswith(
            (
                ".bat",
                ".cfg",
                ".csv",
                ".env",
                ".ini",
                ".js",
                ".json",
                ".log",
                ".md",
                ".py",
                ".sh",
                ".toml",
                ".ts",
                ".txt",
                ".xml",
                ".yaml",
                ".yml",
            )
        )

    return False


def _decode_file_content(data: bytes) -> tuple[str | None, str | None]:
    for encoding in ("utf-8", "utf-8-sig", "cp1256", "latin-1"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue

    return None, None


async def _document_to_dict(client: Client, document) -> dict:
    name = _document_name(document.name)
    mime_type = _document_mime_type(document)
    size = getattr(document, "size", None)

    result = {
        "file_id": document.file_id,
        "access_hash": document.access_hash,
        "size": size,
        "name": name,
        "mime_type": mime_type,
        "caption": document.caption.content if document.caption else None,
        "content": None,
        "content_encoding": None,
        "content_status": "not_downloaded",
        "content_error": None,
    }

    if size is not None and size > MAX_INLINE_FILE_BYTES:
        result["content_status"] = "skipped_too_large"
        return result

    if not _is_text_document(name, mime_type):
        result["content_status"] = "skipped_non_text"
        return result

    try:
        destination = io.BytesIO()
        await client.download_file(
            file_id=document.file_id,
            access_hash=document.access_hash,
            destination=destination,
        )
        data = destination.getvalue()
    except Exception as error:
        result["content_status"] = "download_failed"
        result["content_error"] = f"{type(error).__name__}: {error}"
        return result

    content, encoding = _decode_file_content(data)
    if content is None:
        result["content_status"] = "decode_failed"
        return result

    if len(content) > MAX_INLINE_TEXT_CHARS:
        content = content[:MAX_INLINE_TEXT_CHARS]
        result["content_status"] = "truncated"
    else:
        result["content_status"] = "loaded"

    result["content"] = content
    result["content_encoding"] = encoding
    return result


async def message_to_dict(msg: Message, client: Client | None = None) -> dict:
    """
    Convert aiobale Message object to a JSON-serializable dict.
    """
    document = msg.document
    result = {
        "chat_id": msg.chat.id,
        "chat_type": get_chat_type_value(msg.chat.type),
        "sender_id": msg.sender_id,
        "date_ms": msg.date,
        "message_id": msg.message_id,
        "text": msg.text,
        "has_document": document is not None,
        "document": None,
    }

    if document is not None and client is not None:
        result["document"] = await _document_to_dict(client, document)

    return result
