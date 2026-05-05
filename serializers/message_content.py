from dataclasses import dataclass
from typing import Any

from aiobale.types import Message


@dataclass(frozen=True)
class NormalizedMessageContent:
    text: str | None
    document: Any | None
    is_forwarded: bool
    forwarded_from: dict[str, Any] | None
    content_source: str
    content_note: str | None


def _value_or_none(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value

    return value


def _enum_value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value

    return value


def _content_text(content: Any) -> str | None:
    text = getattr(content, "text", None)
    if text is None:
        return None

    value = getattr(text, "value", None)
    return value if isinstance(value, str) else None


def _content_document(content: Any) -> Any | None:
    return getattr(content, "document", None)


def _forwarded_from_dict(forwarded: Any) -> dict[str, Any]:
    peer = getattr(forwarded, "peer", None)

    result: dict[str, Any] = {
        "message_id": _value_or_none(getattr(forwarded, "message_id", None)),
        "sender_id": getattr(forwarded, "sender_id", None),
        "date_ms": getattr(forwarded, "date", None),
    }

    if peer is not None:
        result["peer"] = {
            "id": getattr(peer, "id", None),
            "type": _enum_value(getattr(peer, "type", None)),
        }

    return result


def normalize_message_content(msg: Message) -> NormalizedMessageContent:
    """
    Return the content Codex should read, whether it is direct or forwarded.

    aiobale exposes forwarded payloads through msg.quoted_replied_to while the
    outer message content is marked empty. Direct content remains on msg.content.
    """
    direct_text = msg.text
    direct_document = msg.document
    if direct_text is not None or direct_document is not None:
        return NormalizedMessageContent(
            text=direct_text,
            document=direct_document,
            is_forwarded=False,
            forwarded_from=None,
            content_source="direct",
            content_note=None,
        )

    forwarded = getattr(msg, "quoted_replied_to", None)
    if forwarded is not None and getattr(getattr(msg, "content", None), "empty", False):
        forwarded_content = getattr(forwarded, "content", None)
        forwarded_text = _content_text(forwarded_content)
        forwarded_document = _content_document(forwarded_content)

        if forwarded_text is not None or forwarded_document is not None:
            note = "forwarded_document" if forwarded_document is not None else "forwarded_text"
            return NormalizedMessageContent(
                text=forwarded_text,
                document=forwarded_document,
                is_forwarded=True,
                forwarded_from=_forwarded_from_dict(forwarded),
                content_source="forwarded",
                content_note=note,
            )

        return NormalizedMessageContent(
            text=None,
            document=None,
            is_forwarded=True,
            forwarded_from=_forwarded_from_dict(forwarded),
            content_source="forwarded",
            content_note="Forwarded message metadata was exposed, but no readable text or document content was present.",
        )

    return NormalizedMessageContent(
        text=None,
        document=None,
        is_forwarded=False,
        forwarded_from=None,
        content_source="direct",
        content_note="Empty/non-text message. No document attached.",
    )
