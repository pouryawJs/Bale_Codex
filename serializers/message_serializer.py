from pathlib import Path

from aiobale import Client
from aiobale.types import Message

from services.documents import document_to_dict


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
    document = msg.document
    return {
        "chat_id": msg.chat.id,
        "chat_type": get_chat_type_value(msg.chat.type),
        "sender_id": msg.sender_id,
        "date_ms": msg.date,
        "message_id": msg.message_id,
        "text": msg.text,
        "has_document": document is not None,
        "document": None,
    }


async def message_to_rich_dict(
    client: Client,
    msg: Message,
    download_dir: Path,
) -> dict:
    """
    Convert aiobale Message object to a JSON-serializable dict with document text.
    """
    result = message_to_dict(msg)
    result["document"] = await document_to_dict(
        client=client,
        msg=msg,
        download_dir=download_dir,
    )
    return result
