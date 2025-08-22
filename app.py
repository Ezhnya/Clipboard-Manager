from __future__ import annotations
import sys
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from database import DB
from clipboard_monitor import ClipboardMonitor
from gui import MainWindow
from config import HOTKEY
from pathlib import Path

def start_hotkey_thread(callback, hotkey: str):
    try:
        import keyboard
    except Exception:
        return
    def worker():
        try:
            keyboard.add_hotkey(hotkey, callback)
            keyboard.wait()
        except Exception:
            pass
    t = threading.Thread(target=worker, daemon=True)
    t.start()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Clipboard Manager")
    icon = QIcon(str(Path(__file__).resolve().parent / "assets" / "icon.png"))
    db = DB()
    win = MainWindow(db, icon)
    win.show()

    mon = ClipboardMonitor(app)
    def on_new(d):
        new_id = db.add_clip(d['type'], d['content'], d['path'], d['ts'], False, d['hash'])
        if new_id is not None:
            win.update_list()
    mon.new_item.connect(on_new)

    start_hotkey_thread(win.bring_to_front, HOTKEY)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
