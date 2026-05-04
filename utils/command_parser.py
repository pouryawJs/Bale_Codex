MAX_REQUESTED_MESSAGES = 2000

def parse_register_chat_command(text: str) -> str:
    parts = text.strip().split(maxsplit=1)

    if len(parts) != 2:
        raise ValueError("Invalid command format. Use: */rc <title>*")

    return parts[1].strip()