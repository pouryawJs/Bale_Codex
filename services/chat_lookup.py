from services.chat_registery import load_registered_chats


class ChatNotFoundError(Exception):
    pass


class AmbiguousChatTitleError(Exception):
    def __init__(self, matches: list[dict]):
        self.matches = matches
        super().__init__("Ambiguous chat title.")


def find_chat_by_title(title: str) -> dict:
    chats = [
        chat for chat in load_registered_chats()
        if chat.get("is_active", True)
    ]

    normalized_title = title.strip().casefold()

    exact_matches = [
        chat for chat in chats
        if chat["title"].strip().casefold() == normalized_title
    ]

    if len(exact_matches) == 1:
        return exact_matches[0]

    if len(exact_matches) > 1:
        raise AmbiguousChatTitleError(exact_matches)

    partial_matches = [
        chat for chat in chats
        if normalized_title in chat["title"].strip().casefold()
    ]

    if len(partial_matches) == 1:
        return partial_matches[0]

    if len(partial_matches) > 1:
        raise AmbiguousChatTitleError(partial_matches)

    raise ChatNotFoundError(f"Chat not found: {title}")