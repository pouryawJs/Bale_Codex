import re


_SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(value: str) -> str:
    """
    Convert user/chat/file provided text into a filesystem-safe filename part.
    """
    cleaned = _SAFE_FILENAME_PATTERN.sub("_", value.strip())
    cleaned = cleaned.strip("._-")

    return cleaned or "untitled"
