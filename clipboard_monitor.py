from __future__ import annotations
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from pathlib import Path
from typing import Optional
from config import IMAGE_DIR
from utils import iso_now, content_hash, is_url
import uuid

class ClipboardMonitor(QObject):
    new_item = Signal(dict)

    def __init__(self, app: QApplication):
        super().__init__()
        self.clipboard = QGuiApplication.clipboard()
        self.clipboard.dataChanged.connect(self._on_changed)
        self._last_hash: Optional[str] = None

    def _on_changed(self):
        md = self.clipboard.mimeData()
        ts = iso_now()

        if md.hasUrls():
            urls = md.urls()
            if urls:
                paths = []
                for u in urls:
                    if u.isLocalFile():
                        paths.append(u.toLocalFile())
                    else:
                        paths.append(u.toString())
                content = '\n'.join(paths)
                h = content_hash('file', content, None)
                if h == self._last_hash: 
                    return
                self._last_hash = h
                self.new_item.emit({'type': 'file', 'content': content, 'path': None, 'ts': ts, 'hash': h})
                return

        if md.hasImage():
            img = self.clipboard.image()
            if not img.isNull():
                IMAGE_DIR.mkdir(parents=True, exist_ok=True)
                from PySide6.QtGui import QImage
                fname = IMAGE_DIR / f"clip_{uuid.uuid4().hex}.png"
                img.save(str(fname), 'PNG')
                h = content_hash('image', '', str(fname))
                if h == self._last_hash:
                    return
                self._last_hash = h
                self.new_item.emit({'type': 'image', 'content': '', 'path': str(fname), 'ts': ts, 'hash': h})
                return

        if md.hasText():
            text = md.text()
            ttype = 'link' if is_url(text.strip()) else 'text'
            h = content_hash(ttype, text, None)
            if h == self._last_hash:
                return
            self._last_hash = h
            self.new_item.emit({'type': ttype, 'content': text, 'path': None, 'ts': ts, 'hash': h})
