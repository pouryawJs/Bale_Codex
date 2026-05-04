from pathlib import Path

from aiobale import Client


async def download_document(
    client: Client,
    file_id: int,
    access_hash: int,
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    await client.download_file(
        file_id=file_id,
        access_hash=access_hash,
        destination=destination,
    )
