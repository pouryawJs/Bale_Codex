from aiobale import Client, Dispatcher
from aiobale.types import Message

from handlers.command_router import handle_command

dp = Dispatcher()
client = Client(dp, show_update_errors=True)


@dp.message()
async def command_handler(msg: Message, client: Client):
    await handle_command(msg=msg, client=client)


client.run()
