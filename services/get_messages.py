import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional

from aiobale import Client
from aiobale.enums import ListLoadMode
from aiobale.types import Message
from pydantic import ValidationError


@dataclass(frozen=True)
class HistoryLoadResult:
    messages: list[Message]
    warnings: list[dict[str, Any]] = field(default_factory=list)
    partial: bool = False
    failed_page_error: str | None = None


def _error_details(error: Exception) -> str:
    details = str(error)
    if len(details) > 1200:
        return f"{details[:1200]}..."

    return details


def _history_validation_warning(
    error: Exception,
    *,
    requested_limit: int,
    failed_limit: int,
    offset_date: int,
) -> dict[str, Any]:
    return {
        "type": "history_page_validation_error",
        "message": (
            "One page of chat history could not be parsed, likely because Bale "
            "returned an unsupported or unexpected payload."
        ),
        "details": _error_details(error),
        "requested_limit": requested_limit,
        "failed_limit": failed_limit,
        "offset_date": offset_date,
    }


async def _load_history_page_safely(
    client: Client,
    chat_id: int,
    chat_type,
    limit: int,
    offset_date: int,
) -> tuple[list[Message], list[dict[str, Any]], bool]:
    """
    Load one history page, reducing the page size when aiobale cannot validate it.

    If even a single-message page fails, aiobale did not expose a usable Message
    object to us, so the caller must stop at that boundary and return partial data.
    """
    current_limit = limit
    warnings: list[dict[str, Any]] = []

    while current_limit >= 1:
        try:
            messages = await client.load_history(
                chat_id=chat_id,
                chat_type=chat_type,
                limit=current_limit,
                offset_date=offset_date,
                load_mode=ListLoadMode.BACKWARD,
            )
            return messages, warnings, False
        except ValidationError as error:
            warnings.append(
                _history_validation_warning(
                    error,
                    requested_limit=limit,
                    failed_limit=current_limit,
                    offset_date=offset_date,
                )
            )

            if current_limit == 1:
                return [], warnings, True

            current_limit = max(1, current_limit // 2)

    return [], warnings, True


async def get_last_n_messages(
    client: Client,
    chat_id: int,
    chat_type,
    n: int,
    status_message: Optional[Message] = None,
    page_size: int = 50,
    exclude_message_id: Optional[int] = None,
) -> HistoryLoadResult:
    """
    Load the last N messages page by page.
    This avoids sending one large history request.
    """

    all_messages = []
    warnings: list[dict[str, Any]] = []
    partial = False
    offset_date = -1
    page_number = 0

    while len(all_messages) < n:
        remaining = n - len(all_messages)
        current_limit = min(page_size, remaining + 1)

        messages, page_warnings, page_failed = await _load_history_page_safely(
            client=client,
            chat_id=chat_id,
            chat_type=chat_type,
            limit=current_limit,
            offset_date=offset_date,
        )
        warnings.extend(page_warnings)

        if page_failed:
            partial = True
            break

        if not messages:
            break

        if exclude_message_id is not None:
            messages = [
                item for item in messages
                if item.message_id != exclude_message_id
            ]

        if not messages:
            break

        page_number += 1
        all_messages.extend(messages)

        oldest = min(messages, key=lambda item: item.date)
        new_offset = oldest.date

        if new_offset == offset_date:
            break

        offset_date = new_offset

        await asyncio.sleep(0.5)

    unique = {}
    for item in all_messages:
        unique[item.message_id] = item

    result = sorted(unique.values(), key=lambda item: item.date)

    partial = partial or bool(warnings)
    failed_page_error = warnings[-1]["details"] if partial and warnings else None

    return HistoryLoadResult(
        messages=result[-n:],
        warnings=warnings,
        partial=partial,
        failed_page_error=failed_page_error,
    )


async def get_all_messages(
    client: Client,
    chat_id: int,
    chat_type,
    status_message: Optional[Message] = None,
    page_size: int = 50,
    exclude_message_id: Optional[int] = None,
) -> HistoryLoadResult:
    """
    Load all chat messages page by page.
    """

    all_messages = []
    warnings: list[dict[str, Any]] = []
    partial = False
    offset_date = -1
    page_number = 0

    while True:
        messages, page_warnings, page_failed = await _load_history_page_safely(
            client=client,
            chat_id=chat_id,
            chat_type=chat_type,
            limit=page_size,
            offset_date=offset_date,
        )
        warnings.extend(page_warnings)

        if page_failed:
            partial = True
            break

        if not messages:
            break

        if exclude_message_id is not None:
            messages = [
                item for item in messages
                if item.message_id != exclude_message_id
            ]

        if not messages:
            break

        page_number += 1
        all_messages.extend(messages)

        oldest = min(messages, key=lambda item: item.date)
        new_offset = oldest.date

        if new_offset == offset_date:
            break

        offset_date = new_offset

        await asyncio.sleep(0.5)

    unique = {}
    for item in all_messages:
        unique[item.message_id] = item

    partial = partial or bool(warnings)
    failed_page_error = warnings[-1]["details"] if partial and warnings else None

    return HistoryLoadResult(
        messages=sorted(unique.values(), key=lambda item: item.date),
        warnings=warnings,
        partial=partial,
        failed_page_error=failed_page_error,
    )
