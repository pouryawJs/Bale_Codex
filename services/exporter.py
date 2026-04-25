from utils.messages_utils import message_to_dict
from datetime import datetime
from aiobale.types import Message
from pathlib import Path
import json

def save_messages_to_json(messages: list[Message], chat_id: int) -> str:
    """
    Save messages into a JSON file.
    """
    Path("exports").mkdir(exist_ok=True)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/chat_{chat_id}_{now}.json"

    data = [message_to_dict(item) for item in messages]

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return filename
