import os


MAX_DOWNLOAD_FILE_SIZE_MB = int(os.getenv("MAX_DOWNLOAD_FILE_SIZE_MB", "10"))
MAX_DOWNLOAD_FILE_BYTES = MAX_DOWNLOAD_FILE_SIZE_MB * 1024 * 1024
MAX_EXTRACTED_CHARS = int(os.getenv("MAX_EXTRACTED_CHARS", "12000"))

TEXT_EXTENSIONS = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".log",
    ".md",
    ".py",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

ARCHIVE_EXTENSIONS = {".7z", ".rar", ".zip"}
IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
VIDEO_EXTENSIONS = {".avi", ".mkv", ".mov", ".mp4", ".webm"}
AUDIO_EXTENSIONS = {".flac", ".m4a", ".mp3", ".ogg", ".wav"}
UNSUPPORTED_BINARY_EXTENSIONS = (
    ARCHIVE_EXTENSIONS | IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS
)
