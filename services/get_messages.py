import asyncio
from typing import Optional
from utils.safe_edit import safe_edit_status
from aiobale import Client
from aiobale.types import Message
from aiobale.enums import ListLoadMode

async def get_last_n_messages(
    client: Client,
    chat_id: int,
    chat_type,
    n: int,
    status_message: Message,
    page_size: int = 50,
    exclude_message_id: Optional[int] = None,
) -> list[Message]:
    """
    Load the last N messages page by page.
    This avoids sending one large history request.
    """

    all_messages = []
    offset_date = -1
    page_number = 0

    while len(all_messages) < n:
        remaining = n - len(all_messages)
        current_limit = min(page_size, remaining + 1)

        messages = await client.load_history(
            chat_id=chat_id,
            chat_type=chat_type,
            limit=current_limit,
            offset_date=offset_date,
            load_mode=ListLoadMode.BACKWARD,
        )

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

        await safe_edit_status(
            status_message,
            (
                "Analyzing chat...\n"
                f"Mode: last {n} messages\n"
                f"Loaded messages: {min(len(all_messages), n)} / {n}\n"
                f"Loaded pages: {page_number}\n"
                f"Page size: {page_size}"
            )
        )

        await asyncio.sleep(0.5)

    unique = {}
    for item in all_messages:
        unique[item.message_id] = item

    result = sorted(unique.values(), key=lambda item: item.date)

    return result[-n:]

async def get_all_messages(
    client: Client,
    chat_id: int,
    chat_type,
    status_message: Message,
    page_size: int = 50,
    exclude_message_id: Optional[int] = None,
) -> list[Message]:
    """
    Load all chat messages page by page.
    Used for /analyz all without a count.
    """

    all_messages = []
    offset_date = -1
    page_number = 0

    while True:
        messages = await client.load_history(
            chat_id=chat_id,
            chat_type=chat_type,
            limit=page_size,
            offset_date=offset_date,
            load_mode=ListLoadMode.BACKWARD,
        )


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

        await safe_edit_status(
            status_message,
            (
                "Analyzing chat...\n"
                f"Loaded messages: {len(all_messages)}\n"
                f"Loaded pages: {page_number}\n"
                f"Page size: {page_size}"
            )
        )

        await asyncio.sleep(0.5)

    unique = {}
    for item in all_messages:
        unique[item.message_id] = item

    return sorted(unique.values(), key=lambda item: item.date)
