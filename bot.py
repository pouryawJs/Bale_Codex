from aiobale import Client, Dispatcher
from aiobale.types import Message
from handlers.analyz_handler import analyz

dp = Dispatcher()
client = Client(dp)

@dp.message()
async def command_handler(msg: Message, client: Client):
    text = msg.text

    if not text:
        return

    if  text.startswith("/analyz"):
        if client.id == msg.sender_id :
            return await analyz(msg=msg, client=client, text=text)
        else :
            return await msg.reply("You have no access to use this command")
    
    return

client.run()