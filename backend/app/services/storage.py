import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from backend.app.config import settings

# Known image magic bytes
MAGIC_NUMBERS = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WebP begins with RIFF....WEBP
}

def detect_mime_type(content_header: bytes) -> str | None:
    if content_header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if content_header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content_header.startswith(b"RIFF") and len(content_header) >= 12 and content_header[8:12] == b"WEBP":
        return "image/webp"
    return None

class LocalStorageService:
    def __init__(self, upload_dir: Path | None = None):
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> tuple[str, str, str, int]:
        """
        Validates and safely stores an uploaded image file.
        Returns: (relative_or_abs_path, original_filename, mime_type, file_size)
        """
        # 1. Check extension
        original_name = file.filename or "unknown.jpg"
        ext = Path(original_name).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension '{ext}'. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # 2. Read contents with size limit
        content = await file.read()
        file_size = len(content)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB."
            )

        # 3. Check MIME signature / magic bytes
        detected_mime = detect_mime_type(content[:32])
        if not detected_mime or detected_mime not in settings.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file signature. File is not a valid JPEG, PNG, or WebP image."
            )

        # 4. Generate safe server-side filename (prevent path traversal)
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        destination = (self.upload_dir / safe_filename).resolve()

        # Ensure destination is strictly inside upload_dir
        if not str(destination).startswith(str(self.upload_dir.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path detected.")

        with open(destination, "wb") as f:
            f.write(content)

        return str(destination), original_name, detected_mime, file_size

storage_service = LocalStorageService()
