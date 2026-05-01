from aiobale import Client
from aiobale.types import Message

from services.chat_registery import register_chat
from utils.safe_edit import safe_edit_status
from utils.messages_utils import get_chat_type_value
from utils.command_parser import parse_register_chat_command

async def register_chat_handler(msg: Message, client: Client, text: str):
    try:
        title = parse_register_chat_command(text)
    except ValueError as e:
        await safe_edit_status(msg, f"{e}")
        return
    
    chat = register_chat(
        title=title,
        chat_id=msg.chat.id,
        chat_type=get_chat_type_value(msg.chat.type),
    )

    await safe_edit_status(
        msg,
        (
            "Chat registered successfully ✅\n"
            f"Title saved as: *{chat['title']} *\n"
            f"Chat ID: *{chat['chat_id']}*\n"
        )
    )