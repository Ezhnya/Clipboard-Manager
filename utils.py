import hashlib
import os
from pathlib import Path
from datetime import datetime

def iso_now() -> str:
    return datetime.now().isoformat(timespec='seconds')

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def content_hash(type_: str, content: str, path: str | None) -> str:
    h = hashlib.sha256()
    h.update(type_.encode())
    if content:
        h.update(content.encode(errors='ignore'))
    if path:
        try:
            size = os.path.getsize(path)
            h.update(str(size).encode())
        except OSError:
            h.update(path.encode())
    return h.hexdigest()

def is_url(text: str) -> bool:
    return text.startswith('http://') or text.startswith('https://')

def preview_text(text: str, limit: int = 120) -> str:
    t = ' '.join(text.strip().split())
    return t if len(t) <= limit else t[:limit - 1] + '…'
