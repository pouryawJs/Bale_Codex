from aiobale import Client

from services.chat_lookup import find_chat_by_title


async def send_message_by_title(
    client: Client,
    chat_title: str,
    text: str,
) -> dict:
    chat = find_chat_by_title(chat_title)

    await client.send_message(
        chat_id=chat["chat_id"],
        chat_type=chat["chat_type"],
        text=text,
    )

    return {
        "ok": True,
        "chat_title": chat["title"],
        "chat_id": chat["chat_id"],
        "chat_type": chat["chat_type"],
    }