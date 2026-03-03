import re
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
CHUNK_SIZE = 1024 * 1024  # 1MB


def sanitize_filename(filename: str) -> str:
    safe_name = Path(filename or "").name
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", safe_name)
    if not safe_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Invalid filename"})
    return safe_name


def validate_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid file type. Only .csv and .xlsx are allowed."},
        )
    return suffix


def dataset_storage_dir(organization_id: UUID, dataset_id: UUID) -> Path:
    settings = get_settings()
    return Path(settings.STORAGE_ROOT) / str(organization_id) / str(dataset_id)


async def save_upload_file(organization_id: UUID, dataset_id: UUID, upload_file: UploadFile) -> tuple[str, int]:
    filename = sanitize_filename(upload_file.filename or "")
    validate_extension(filename)

    storage_dir = dataset_storage_dir(organization_id, dataset_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    destination = (storage_dir / filename).resolve()

    max_bytes = get_settings().MAX_UPLOAD_SIZE_MB * 1024 * 1024
    written = 0

    try:
        with destination.open("wb") as target:
            while True:
                chunk = await upload_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={"message": f"File too large. Max size is {get_settings().MAX_UPLOAD_SIZE_MB}MB."},
                    )
                target.write(chunk)
    except Exception:
        if destination.exists():
            destination.unlink(missing_ok=True)
        if storage_dir.exists() and not any(storage_dir.iterdir()):
            storage_dir.rmdir()
        raise
    finally:
        await upload_file.close()

    return str(destination), written
