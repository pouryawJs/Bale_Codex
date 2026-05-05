from pathlib import Path

from aiobale import Client
from aiobale.types import Message

from services.documents import document_to_dict
from serializers.message_content import normalize_message_content


def get_chat_type_value(chat_type) -> int:
    """
    Convert chat type to int safely.
    It supports both raw int and Enum-like values.
    """
    if hasattr(chat_type, "value"):
        return int(chat_type.value)

    return int(chat_type)


def message_to_dict(msg: Message, client: Client | None = None) -> dict:
    """
    Convert aiobale Message object to a JSON-serializable dict.
    """
    normalized = normalize_message_content(msg)
    return {
        "chat_id": msg.chat.id,
        "chat_type": get_chat_type_value(msg.chat.type),
        "sender_id": msg.sender_id,
        "date_ms": msg.date,
        "message_id": msg.message_id,
        "text": normalized.text,
        "has_document": normalized.document is not None,
        "document": None,
        "is_forwarded": normalized.is_forwarded,
        "forwarded_from": normalized.forwarded_from,
        "content_source": normalized.content_source,
        "content_note": normalized.content_note,
    }


async def message_to_rich_dict(
    client: Client,
    msg: Message,
    download_dir: Path,
) -> dict:
    """
    Convert aiobale Message object to a JSON-serializable dict with document text.
    """
    normalized = normalize_message_content(msg)
    result = message_to_dict(msg)
    result["document"] = await document_to_dict(
        client=client,
        msg=msg,
        download_dir=download_dir,
        document=normalized.document,
        content_source=normalized.content_source,
    )
    return result
