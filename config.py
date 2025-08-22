from pathlib import Path

APP_NAME = "Clipboard Manager"
APP_ID = "clipboard_manager"
MAX_ITEMS = 1000
THEME = "dark"  # 'light' or 'dark'
HOTKEY = "ctrl+shift+v"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = DATA_DIR / "images"
DB_PATH = BASE_DIR / "clipboard.db"

PREVIEW_TRUNC = 120
TRAY_SHOW_RECENTS = 8
