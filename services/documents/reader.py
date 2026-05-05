from pathlib import Path

from aiobale import Client
from aiobale.types import Message

from services.documents.constants import (
    MAX_DOWNLOAD_FILE_BYTES,
    MAX_DOWNLOAD_FILE_SIZE_MB,
    MAX_EXTRACTED_CHARS,
    UNSUPPORTED_BINARY_EXTENSIONS,
)
from services.documents.downloader import download_document
from services.documents.metadata import (
    document_caption,
    document_mime_type,
    document_name,
)
from services.documents.parsers import (
    extract_text_from_file,
    unsupported_extraction_result,
)
from utils.path_utils import safe_filename


async def document_to_dict(
    client: Client,
    msg: Message,
    download_dir: Path,
    document=None,
    content_source: str = "direct",
) -> dict | None:
    if document is None:
        document = msg.document
    if document is None:
        return None

    name = document_name(getattr(document, "name", None))
    safe_name = safe_filename(name or f"file_{document.file_id}")
    local_path = download_dir / f"{msg.message_id}_{safe_name}"
    size = getattr(document, "size", None)
    mime_type = document_mime_type(document, name)
    suffix = local_path.suffix.lower()

    result = {
        "content_source": content_source,
        "file_id": document.file_id,
        "access_hash": document.access_hash,
        "name": name,
        "size": size,
        "mime_type": mime_type,
        "caption": document_caption(document),
        "local_path": None,
        "downloaded": False,
        "extracted_text": None,
        "extraction_error": None,
        "truncated": False,
        "parser": None,
    }

    if suffix in UNSUPPORTED_BINARY_EXTENSIONS:
        result.update(unsupported_extraction_result())
        return result

    if size is not None and size > MAX_DOWNLOAD_FILE_BYTES:
        result["extraction_error"] = (
            f"File is larger than MAX_DOWNLOAD_FILE_SIZE_MB "
            f"({MAX_DOWNLOAD_FILE_SIZE_MB} MB); download skipped."
        )
        return result

    try:
        await download_document(
            client=client,
            file_id=document.file_id,
            access_hash=document.access_hash,
            destination=local_path,
        )
        result["downloaded"] = True
        result["local_path"] = str(local_path)
    except Exception as error:
        result["extraction_error"] = f"Download failed: {type(error).__name__}: {error}"
        return result

    extraction = extract_text_from_file(
        path=local_path,
        mime_type=mime_type,
        max_chars=MAX_EXTRACTED_CHARS,
    )
    result.update(extraction)
    return result
