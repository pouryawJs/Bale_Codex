from typing import Any

from mcp.server.fastmcp import FastMCP

from interfaces.mcp_support.tools import (
    list_registered_chats,
    read_registered_chat_messages,
    send_registered_chat_message,
)


mcp = FastMCP("bale-codex")


@mcp.tool()
def bale_list_chats() -> dict[str, Any]:
    """
    List all registered Bale chats.
    """
    return list_registered_chats()


@mcp.tool()
async def bale_read_messages(
    chat_title: str,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Read recent messages from a registered Bale chat by title.
    """
    return await read_registered_chat_messages(chat_title=chat_title, limit=limit)


@mcp.tool()
async def bale_send_message(
    chat_title: str,
    text: str,
) -> dict[str, Any]:
    """
    Send a text message to a registered Bale chat by title.
    """
    return await send_registered_chat_message(chat_title=chat_title, text=text)


if __name__ == "__main__":
    mcp.run()
