from aiobale import Client, Dispatcher
from aiobale.types import Message
from handlers.analyz_handler import analyz
from handlers.register_chat_handler import register_chat_handler

dp = Dispatcher()
client = Client(dp, show_update_errors=True)

@dp.message()
async def command_handler(msg: Message, client: Client):
    text = msg.text
    if not text:
        return

    if text.startswith("/analyz"):
        if client.id == msg.sender_id :
            return await analyz(msg=msg, client=client, text=text)
        else :
            return await msg.reply("You have no access to use this command")
        
    if text.startswith("/rc"):
        if client.id == msg.sender_id:
            return await register_chat_handler(msg=msg, client=client, text=text)
        else: 
            return await msg.reply("You have no access to use this command")
    
    return 

client.run()