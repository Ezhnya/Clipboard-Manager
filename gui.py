from __future__ import annotations
from PySide6.QtCore import Qt, QSortFilterProxyModel, QRegularExpression, QModelIndex, QAbstractTableModel
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QTableView, QHeaderView, QPushButton, QMessageBox, QMenu, QLabel, QSystemTrayIcon
)
from models import ClipItem
from database import DB
from utils import preview_text
from config import PREVIEW_TRUNC, THEME, TRAY_SHOW_RECENTS
from pathlib import Path
import os
import webbrowser
from PySide6.QtWidgets import QAbstractItemView

class ClipModel(QAbstractTableModel):
    headers = ["Type", "Preview / Path", "Time", "★"]

    def __init__(self, rows: list[ClipItem]):
        super().__init__()
        self.rows = rows

    def rowCount(self, parent=None): return len(self.rows)
    def columnCount(self, parent=None): return 4

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid(): return None
        item = self.rows[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return item.type
            elif col == 1:
                if item.type == 'image' and item.path:
                    return f"[image] {Path(item.path).name}"
                return preview_text(item.content, PREVIEW_TRUNC)
            elif col == 2:
                return item.ts.replace('T', ' ')
            elif col == 3:
                return '★' if item.favorite else ''
        if role == Qt.ToolTipRole:
            if item.type == 'image' and item.path:
                return item.path
            return item.content
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def update_rows(self, rows: list[ClipItem]):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

class TypeFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.type_filter = "all"

    def set_type_filter(self, t: str):
        self.type_filter = t
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if super().filterAcceptsRow(source_row, source_parent) is False:
            return False
        if self.type_filter == "all":
            return True
        idx = self.sourceModel().index(source_row, 0, source_parent)
        item_type = self.sourceModel().data(idx, Qt.DisplayRole)
        return item_type.lower() == self.type_filter

class MainWindow(QMainWindow):
    def __init__(self, db: DB, icon: QIcon):
        super().__init__()
        self.db = db
        self.setWindowTitle("Clipboard Manager")
        self.setWindowIcon(icon)
        self.resize(900, 560)

        container = QWidget()
        layout = QVBoxLayout(container)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Пошук в історії…")
        self.filter = QComboBox()
        self.filter.addItems(["All", "Text", "Link", "Image", "File"])
        self.clear_btn = QPushButton("Очистити (без обраних)")
        top.addWidget(self.search, 2)
        top.addWidget(self.filter, 0)
        top.addWidget(self.clear_btn, 0)
        layout.addLayout(top)

        self.table = QTableView()
        self.model = ClipModel(self.db.list_clips())
        self.proxy = TypeFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        self.preview = QLabel("")
        self.preview.setWordWrap(True)
        self.preview.setMinimumHeight(60)
        layout.addWidget(self.preview)

        self.setCentralWidget(container)

        self.search.textChanged.connect(self.apply_filters)
        self.filter.currentIndexChanged.connect(self.apply_filters)
        self.clear_btn.clicked.connect(self.clear_history)
        self.table.doubleClicked.connect(self.copy_selected_back)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.row_context_menu)
        self.table.selectionModel().selectionChanged.connect(self.update_preview)

        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Clipboard Manager")
        self.tray_menu = QMenu()
        self.action_show = QAction("Відкрити")
        self.action_quit = QAction("Вийти")
        self.recent_menu = QMenu("Останні")
        self.tray_menu.addMenu(self.recent_menu)
        self.tray_menu.addAction(self.action_show)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.action_quit)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.action_show.triggered.connect(self.bring_to_front)
        self.action_quit.triggered.connect(self.close)
        self.tray.show()
        self.refresh_recent_in_tray()

        if THEME == 'dark':
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: #eaeaea; }
                QLabel, QLineEdit, QComboBox, QTableView, QPushButton { color: #eaeaea; }
                QLineEdit, QComboBox, QTableView { background-color: #1e1e1e; border: 1px solid #2a2a2a; }
                QPushButton { background-color: #2a2a2a; border: 1px solid #3a3a3a; padding: 6px 10px; border-radius: 8px; }
                QPushButton:hover { background-color: #3a3a3a; }
            """)

        if THEME == 'light':
            self.setStyleSheet("""
                QMainWindow { background-color: #f5f5f5; color: #202020; }
                QLabel, QLineEdit, QComboBox, QTableView, QPushButton { color: #202020; }
                QLineEdit, QComboBox, QTableView { background-color: #ffffff; border: 1px solid #cccccc; }
                QPushButton { background-color: #e0e0e0; border: 1px solid #b0b0b0; padding: 6px 10px; border-radius: 8px; }
                QPushButton:hover { background-color: #d0d0d0; }
            """)

    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            event.ignore()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.bring_to_front()

    def bring_to_front(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def apply_filters(self):
        text = self.search.text()
        self.proxy.setFilterRegularExpression(QRegularExpression(text))
        f = self.filter.currentText().lower()
        self.proxy.set_type_filter(f if f in ('text','link','image','file') else 'all')

    def update_list(self):
        self.model.update_rows(self.db.list_clips())
        self.refresh_recent_in_tray()

    def update_preview(self):
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            self.preview.setText("")
            return
        src_index = self.proxy.mapToSource(idxs[0])
        item = self.model.rows[src_index.row()]
        if item.type == 'image' and item.path:
            self.preview.setText(f"Зображення: {item.path}")
        else:
            self.preview.setText(item.content)

    def selected_item(self) -> ClipItem | None:
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            return None
        src_index = self.proxy.mapToSource(idxs[0])
        return self.model.rows[src_index.row()]

    def copy_selected_back(self, *_):
        item = self.selected_item()
        if not item: return
        cb = QApplication.clipboard()
        if item.type == 'image' and item.path:
            from PySide6.QtGui import QImage
            img = QImage(item.path)
            if img.isNull():
                QMessageBox.warning(self, "Помилка", "Не вдалося завантажити зображення.")
                return
            cb.setImage(img)
        else:
            cb.setText(item.content)
        self.statusBar().showMessage("Скопійовано в буфер", 1500)

    def row_context_menu(self, pos):
        idx = self.table.indexAt(pos)
        if not idx.isValid():
            return
        src_index = self.proxy.mapToSource(idx)
        item = self.model.rows[src_index.row()]

        m = QMenu(self)
        act_copy = m.addAction("Скопіювати")
        act_fav = m.addAction("Закріпити" if not item.favorite else "Відкріпити")
        act_del = m.addAction("Видалити")
        if item.type in ('file', 'image'):
            m.addSeparator()
            act_open = m.addAction("Відкрити файл/папку")
        else:
            act_open = None

        action = m.exec_(self.table.viewport().mapToGlobal(pos))
        if action == act_copy:
            self.copy_selected_back()
        elif action == act_fav:
            new_val = self.db.toggle_favorite(item.id)
            self.update_list()
        elif action == act_del:
            self.db.delete(item.id)
            self.update_list()
        elif act_open and action == act_open:
            if item.type == 'image' and item.path:
                path = item.path
            else:
                path = item.content.splitlines()[0]
            if os.path.exists(path):
                os.startfile(path) if os.name == 'nt' else webbrowser.open(f'file://{path}')
            else:
                QMessageBox.information(self, "Файл", "Файл/папка не існує.")

    def clear_history(self):
        if QMessageBox.question(self, "Очистити", "Видалити всі НЕ закріплені записи?") == QMessageBox.Yes:
            self.db.clear(keep_favorites=True)
            self.update_list()

    def refresh_recent_in_tray(self):
        self.recent_menu.clear()
        for it in self.db.recent(TRAY_SHOW_RECENTS):
            label = f"{'★ ' if it.favorite else ''}{it.type}: "
            label += (Path(it.path).name if it.type == 'image' and it.path else preview_text(it.content, 40))
            act = self.recent_menu.addAction(label)
            act.triggered.connect(lambda checked=False, _id=it.id: self._tray_copy(_id))

    def _tray_copy(self, id_: int):
        for it in self.model.rows:
            if it.id == id_:
                cb = QApplication.clipboard()
                if it.type == 'image' and it.path:
                    from PySide6.QtGui import QImage
                    img = QImage(it.path)
                    if not img.isNull():
                        cb.setImage(img)
                else:
                    cb.setText(it.content)
                self.statusBar().showMessage("Скопійовано з трею", 1500)
                break
