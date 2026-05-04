from typing import Any

from services.chat_lookup import AmbiguousChatTitleError, ChatNotFoundError


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
