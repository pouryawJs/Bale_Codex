import logging

from aiobale.types import Message


logger = logging.getLogger(__name__)

async def safe_edit_status(msg: Message, text: str) -> None:
    """
    Edit the command message safely.
    If no status message exists, skip editing.
    If editing fails, log the error instead of writing to stdout.
    """
    if msg is None:
        return

    try:
        await msg.edit_text(text)
    except Exception:
        logger.warning("Failed to edit status message", exc_info=True)
