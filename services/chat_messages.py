from aiobale import Client
from aiobale.types import Message

from services.chat_lookup import find_chat_by_title
from services.get_messages import get_last_n_messages


async def read_messages_by_title(
    client: Client,
    chat_title: str,
    limit: int,
    status_message: Message | None = None,
) -> list[Message]:
    chat = find_chat_by_title(chat_title)

    return await get_last_n_messages(
        client=client,
        chat_id=chat["chat_id"],
        chat_type=chat["chat_type"],
        n=limit,
        status_message=status_message,
        page_size=50,
        exclude_message_id=None,
    )