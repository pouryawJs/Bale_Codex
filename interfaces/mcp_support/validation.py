from typing import Any


MAX_MCP_READ_LIMIT = 300
MAX_MCP_MESSAGE_TEXT_LENGTH = 4000


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

    if limit > MAX_MCP_READ_LIMIT:
        return {
            "ok": False,
            "error_type": "limit_too_large",
            "message": f"Maximum allowed limit is {MAX_MCP_READ_LIMIT}.",
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

    if len(text) > MAX_MCP_MESSAGE_TEXT_LENGTH:
        return {
            "ok": False,
            "error_type": "message_too_long",
            "message": (
                "Message text is too long. "
                f"Maximum length is {MAX_MCP_MESSAGE_TEXT_LENGTH} characters."
            ),
        }

    return None
