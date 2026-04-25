from aiobale.types import Message

def get_chat_type_value(chat_type) -> int:
    """
    Convert chat type to int safely.
    It supports both raw int and Enum-like values.
    """
    if hasattr(chat_type, "value"):
        return int(chat_type.value)

    return int(chat_type)

def message_to_dict(msg: Message) -> dict:
    """
    Convert aiobale Message object to a JSON-serializable dict.
    """
    return {
        "chat_id": msg.chat.id,
        "chat_type": get_chat_type_value(msg.chat.type),
        "sender_id": msg.sender_id,
        "date_ms": msg.date,
        "message_id": msg.message_id,
        "text": msg.text,
        "has_document": msg.document is not None,
    }
