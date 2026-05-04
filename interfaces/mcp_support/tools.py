from pathlib import Path
from typing import Any

from interfaces.mcp_support.client import get_client
from interfaces.mcp_support.errors import format_tool_error
from interfaces.mcp_support.validation import validate_limit, validate_send_text
from serializers.message_serializer import message_to_rich_dict
from services.chat_lookup import find_chat_by_title
from services.chat_messages import read_messages_by_title
from services.chat_registry import load_registered_chats
from utils.path_utils import safe_filename


def list_registered_chats() -> dict[str, Any]:
    """
    List all active registered Bale chats.
    """
    try:
        chats = load_registered_chats()

        active_chats = [
            {
                "title": chat["title"],
                "chat_id": chat["chat_id"],
                "chat_type": chat["chat_type"],
                "is_active": chat.get("is_active", True),
            }
            for chat in chats
            if chat.get("is_active", True)
        ]

        return {
            "ok": True,
            "count": len(active_chats),
            "chats": active_chats,
        }
    except Exception as error:
        return format_tool_error(error)


async def read_registered_chat_messages(
    chat_title: str,
    limit: int,
) -> dict[str, Any]:
    """
    Read recent messages from a registered Bale chat by title.
    """
    try:
        limit_error = validate_limit(limit)
        if limit_error is not None:
            return limit_error

        client = await get_client()

        messages = await read_messages_by_title(
            client=client,
            chat_title=chat_title,
            limit=limit,
        )

        download_dir = Path("downloads") / safe_filename(chat_title)
        rich_messages = []
        for message in messages:
            rich_messages.append(
                await message_to_rich_dict(
                    client=client,
                    msg=message,
                    download_dir=download_dir,
                )
            )

        return {
            "ok": True,
            "chat_title": chat_title,
            "requested_limit": limit,
            "message_count": len(messages),
            "messages": rich_messages,
            "instruction": (
                "When summarizing or analyzing these messages, use both each "
                "message.text value and document.extracted_text when present."
            ),
        }
    except Exception as error:
        return format_tool_error(error)


async def send_registered_chat_message(
    chat_title: str,
    text: str,
) -> dict[str, Any]:
    """
    Send a text message to a registered Bale chat by title.
    """
    try:
        text_error = validate_send_text(text)
        if text_error is not None:
            return text_error

        chat = find_chat_by_title(chat_title)
        client = await get_client()
        sent_text = text.strip()

        await client.send_message(
            text=sent_text,
            chat_id=chat["chat_id"],
            chat_type=chat["chat_type"],
        )

        return {
            "ok": True,
            "chat_title": chat["title"],
            "chat_id": chat["chat_id"],
            "chat_type": chat["chat_type"],
            "sent_text": sent_text,
        }
    except Exception as error:
        return format_tool_error(error)
