# 📋 Clipboard Manager

**Clipboard Manager** is a utility for managing your clipboard history.  
It stores texts, links, files, and images, and allows you to easily search and restore them back into the clipboard.

---

## 🚀 Features
- ✅ Clipboard history for:
  - Text
  - Links
  - Files (file paths)
  - Images (saved locally)
- ✅ Modern graphical interface (**PySide6**, Qt6)
- ✅ Full-text search and type filters
- ✅ Double-click to restore item to clipboard
- ✅ Context menu:
  - Copy back to clipboard
  - Pin / Unpin
  - Delete
  - Open file or folder
- ✅ Tray icon with quick access to recent items
- ✅ Global hotkey (`Ctrl+Shift+V`) to bring up the app
- ✅ SQLite database for reliable history storage
- ✅ Dark theme for a clean, modern look

---

## 🛠 Tech Stack
- Python 3.10+  
- [PySide6](https://pypi.org/project/PySide6/) — GUI (Qt6)  
- [keyboard](https://pypi.org/project/keyboard/) — global hotkeys  
- [SQLite](https://www.sqlite.org/) — database  
- Python standard libraries  

---

## 📂 Project Structure
clipboard_manager/
│── app.py # Entry point
│── gui.py # GUI (PySide6)
│── clipboard_monitor.py# Clipboard monitoring
│── database.py # SQLite database logic
│── models.py # Data models
│── utils.py # Helper functions
│── config.py # Settings (theme, hotkeys, limits)
│── assets/ # Icons, screenshots
│── data/images/ # Saved images
│── requirements.txt # Dependencies
│── README.md # Documentation

2. Install dependencies
pip install -r requirements.txt
⚠️ Note: If PySide6 fails on Python 3.13, use Python 3.12 (recommended).

3.⚙️ Configuration
You can tweak settings inside config.py:
-Maximum number of stored history items
-Path to the SQLite database
-Global hotkey (default: Ctrl+Shift+V)
-Theme (dark / light)

👤 Author

Developed with ❤️ by Ezhnya
GitHub | Telegram

📜 License

This project is free for educational and personal use.
Please credit the author: © 2025 Ezhnya