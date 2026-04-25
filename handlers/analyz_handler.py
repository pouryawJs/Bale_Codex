import asyncio
from aiobale import Client
from aiobale.types import Message
from services.get_messages import get_all_messages , get_last_n_messages
from services.exporter import save_messages_to_json
from utils.safe_edit import safe_edit_status
from utils.command_parser import parse_analyz_command

async def analyz(msg: Message, client: Client,  text: str) :
    try:
        count = parse_analyz_command(text)
    except ValueError as e:
        await safe_edit_status(msg, f"Error: {e}")
        return

    chat_id = msg.chat.id
    chat_type = msg.chat.type

    try:
        if count is None:
            await safe_edit_status(
                msg,
                (
                    "Analyzing chat...\n"
                    "Mode: full history\n"
                    "Page size: 50"
                )
            )
            await asyncio.sleep(1)

            messages = await get_all_messages(
                client=client,
                chat_id=chat_id,
                chat_type=chat_type,
                status_message=msg,
                page_size=50,
                exclude_message_id=msg.message_id,
            )

        else:
            await safe_edit_status(
                msg,
                (
                    "Analyzing chat...\n"
                    f"Mode: last {count} messages"
                )
            )
            await asyncio.sleep(1.5)

            messages = await get_last_n_messages(
            client=client,
            chat_id=chat_id,
            chat_type=chat_type,
            n=count,
            status_message=msg,
            page_size=50,
            exclude_message_id=msg.message_id,
        )

        filename = save_messages_to_json(messages, chat_id)

        await safe_edit_status(
            msg,
            (
                "Analysis completed.\n"
                f"Saved messages: {len(messages)}\n"
            )
        )

    except Exception as e:
        await safe_edit_status(msg, f"Error: {e}")

