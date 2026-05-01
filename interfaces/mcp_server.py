import logging
import sys
from typing import Any

import aiohttp
from mcp.server.fastmcp import FastMCP
from aiobale import Client
from aiobale.client.session.aiohttp import AiohttpSession
from aiobale.logger import logger as aiobale_logger
from aiobale.utils.protobuf import ProtoBuf

from services.chat_registery import load_registered_chats
from services.chat_lookup import (
    ChatNotFoundError,
    AmbiguousChatTitleError,
    find_chat_by_title,
)
from services.chat_messages import read_messages_by_title
from utils.messages_utils import message_to_dict


mcp = FastMCP("bale-codex")

_client: Client | None = None


def configure_aiobale_for_mcp() -> None:
    """
    Keep third-party logs away from MCP stdout.
    """
    aiobale_logger.propagate = False

    for handler in aiobale_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream = sys.stderr

    if not hasattr(AiohttpSession, "_mcp_safe_listen"):
        async def _listen_without_stdout(self) -> None:
            try:
                async for msg in self.ws:
                    if msg.type != aiohttp.WSMsgType.BINARY:
                        continue

                    import asyncio

                    asyncio.create_task(self._handle_received_data(msg.data))
            except Exception:
                aiobale_logger.exception("WebSocket listening failed")
            finally:
                self._running = False

        AiohttpSession._mcp_safe_listen = AiohttpSession._listen
        AiohttpSession._listen = _listen_without_stdout

    if not hasattr(ProtoBuf, "_mcp_safe_fix_fields"):
        def _fix_fields_without_stdout(self, data: Any, raw_message_bytes: bytes) -> Any:
            if isinstance(data, dict):
                try:
                    from aiobale.utils.protobuf import _parse_protobuf_fields, _is_valid_text

                    entries = _parse_protobuf_fields(raw_message_bytes)
                except Exception:
                    return data

                new_data: dict[str, Any] = {}

                for key, value in data.items():
                    pure_key = key.split("-")[0]
                    candidates = [entry for entry in entries if entry[0] == int(pure_key) and entry[1] == 2]

                    fixed: str | None = None
                    if candidates:
                        raw_value = candidates[0][2]
                        try:
                            text = raw_value.decode("utf-8")
                        except UnicodeDecodeError:
                            text = raw_value.decode("latin-1", errors="ignore")
                        if _is_valid_text(text):
                            fixed = text

                    if fixed is not None:
                        new_data[key] = fixed
                    elif isinstance(value, dict) and candidates:
                        new_data[key] = self._fix_fields(value, candidates[0][2])
                    elif isinstance(value, list):
                        new_data[key] = [
                            self._fix_fields(item, raw_message_bytes)
                            for item in value
                        ]
                    else:
                        new_data[key] = value

                return new_data

            if isinstance(data, list):
                return [self._fix_fields(item, raw_message_bytes) for item in data]

            return data

        ProtoBuf._mcp_safe_fix_fields = ProtoBuf._fix_fields
        ProtoBuf._fix_fields = _fix_fields_without_stdout


async def get_client() -> Client:
    """
    Create and reuse a single aiobale client instance.
    """
    global _client

    if _client is None:
        configure_aiobale_for_mcp()
        _client = Client()
        await _client.__aenter__()

    return _client


def format_tool_error(error: Exception) -> dict[str, Any]:
    """
    Convert known project errors into structured MCP responses.
    """
    if isinstance(error, ChatNotFoundError):
        return {
            "ok": False,
            "error_type": "chat_not_found",
            "message": str(error),
        }

    if isinstance(error, AmbiguousChatTitleError):
        return {
            "ok": False,
            "error_type": "ambiguous_chat_title",
            "message": "More than one registered chat matched this title.",
            "matches": [
                {
                    "title": chat["title"],
                    "chat_id": chat["chat_id"],
                    "chat_type": chat["chat_type"],
                }
                for chat in error.matches
            ],
        }

    return {
        "ok": False,
        "error_type": type(error).__name__,
        "message": str(error),
    }


def validate_limit(limit: int) -> dict[str, Any] | None:
    """
    Validate read message limit.
    """
    if limit <= 0:
        return {
            "ok": False,
            "error_type": "invalid_limit",
            "message": "Limit must be greater than zero.",
        }

    if limit > 300:
        return {
            "ok": False,
            "error_type": "limit_too_large",
            "message": "Maximum allowed limit is 300.",
        }

    return None


def validate_send_text(text: str) -> dict[str, Any] | None:
    """
    Validate outgoing message text.
    """
    if not text or not text.strip():
        return {
            "ok": False,
            "error_type": "empty_message",
            "message": "Message text cannot be empty.",
        }

    if len(text) > 4000:
        return {
            "ok": False,
            "error_type": "message_too_long",
            "message": "Message text is too long. Maximum length is 4000 characters.",
        }

    return None


@mcp.tool()
def bale_list_chats() -> dict[str, Any]:
    """
    List all registered Bale chats.
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


@mcp.tool()
async def bale_read_messages(
    chat_title: str,
    limit: int = 50,
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

        return {
            "ok": True,
            "chat_title": chat_title,
            "requested_limit": limit,
            "message_count": len(messages),
            "messages": [
                message_to_dict(message)
                for message in messages
            ],
        }

    except Exception as error:
        return format_tool_error(error)


@mcp.tool()
async def bale_send_message(
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

        await client.send_message(
            text=text.strip(),
            chat_id=chat["chat_id"],
            chat_type=chat["chat_type"],
        )

        return {
            "ok": True,
            "chat_title": chat["title"],
            "chat_id": chat["chat_id"],
            "chat_type": chat["chat_type"],
            "sent_text": text.strip(),
        }

    except Exception as error:
        return format_tool_error(error)


if __name__ == "__main__":
    mcp.run()
