import json
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path


REGISTRY_FILE = Path("data/registered_chats.json")


def _ensure_registry_file() -> None:
    """
    Ensure registry directory and file exist.
    If the file does not exist, create it with an empty JSON list.
    """
    REGISTRY_FILE.parent.mkdir(exist_ok=True)

    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text("[]", encoding="utf-8")
        return

    if REGISTRY_FILE.stat().st_size == 0:
        REGISTRY_FILE.write_text("[]", encoding="utf-8")


def load_registered_chats() -> list[dict]:
    """
    Load registered chats from JSON file.
    If the file is empty or corrupted, reset it to an empty list.
    """
    _ensure_registry_file()

    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            REGISTRY_FILE.write_text("[]", encoding="utf-8")
            return []

        return data

    except JSONDecodeError:
        REGISTRY_FILE.write_text("[]", encoding="utf-8")
        return []


def save_registered_chats(chats: list[dict]) -> None:
    """
    Save registered chats to JSON file.
    """
    _ensure_registry_file()

    with open(REGISTRY_FILE, "w", encoding="utf-8") as file:
        json.dump(chats, file, ensure_ascii=False, indent=2)


def register_chat(title: str, chat_id: int, chat_type: int) -> dict:
    """
    Register or update a chat by chat_id and chat_type.
    """
    chats = load_registered_chats()

    now = datetime.now().isoformat(timespec="seconds")

    new_chat = {
        "title": title,
        "chat_id": chat_id,
        "chat_type": chat_type,
        "created_at": now,
        "updated_at": now,
        "is_active": True,
    }

    for index, chat in enumerate(chats):
        if chat["chat_id"] == chat_id and chat["chat_type"] == chat_type:
            chats[index] = {
                **chat,
                "title": title,
                "updated_at": now,
                "is_active": True,
            }
            save_registered_chats(chats)
            return chats[index]

    chats.append(new_chat)
    save_registered_chats(chats)

    return new_chat
