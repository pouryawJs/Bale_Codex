from aiobale import Client
from aiobale.types import Message

from handlers.register_chat_handler import register_chat_handler


REGISTER_CHAT_COMMANDS = ("/rc", "/register_chat")


def is_owner_command(client: Client, msg: Message) -> bool:
    return client.id == msg.sender_id


async def handle_command(msg: Message, client: Client) -> None:
    text = msg.text
    if not text:
        return

    if text.startswith(REGISTER_CHAT_COMMANDS):
        if is_owner_command(client, msg):
            await register_chat_handler(msg=msg, client=client, text=text)
            return

        await msg.reply("You have no access to use this command")
