import logging
import sys
from typing import Any

import aiohttp
from aiobale import Client
from aiobale.client.session.aiohttp import AiohttpSession
from aiobale.logger import logger as aiobale_logger
from aiobale.types.message_content import DocumentMessage
from aiobale.utils.protobuf import ProtoBuf


_client: Client | None = None


def configure_aiobale_for_mcp() -> None:
    """
    Keep third-party logs and aiobale internals away from MCP stdout.
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
                    from aiobale.utils.protobuf import _is_valid_text, _parse_protobuf_fields

                    entries = _parse_protobuf_fields(raw_message_bytes)
                except Exception:
                    return data

                new_data: dict[str, Any] = {}

                for key, value in data.items():
                    pure_key = key.split("-")[0]
                    candidates = [
                        entry
                        for entry in entries
                        if entry[0] == int(pure_key) and entry[1] == 2
                    ]

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

    if not hasattr(DocumentMessage, "_mcp_safe_default_mime_type"):
        DocumentMessage._mcp_safe_default_mime_type = True
        DocumentMessage.model_fields["mime_type"].default = "application/octet-stream"
        DocumentMessage.model_rebuild(force=True)


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
