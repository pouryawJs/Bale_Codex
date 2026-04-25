from aiobale.types import Message

async def safe_edit_status(msg: Message, text: str) -> None:
    """
    Edit the command message safely.
    If editing fails, it prints the error instead of stopping the whole process.
    """
    try:
        await msg.edit_text(text)
    except Exception as e:
        print(f"Failed to edit status message: {e}")
