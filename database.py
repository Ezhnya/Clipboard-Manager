import sqlite3
from pathlib import Path
from typing import Optional
from models import ClipItem
from config import DB_PATH, MAX_ITEMS

SCHEMA = """
CREATE TABLE IF NOT EXISTS clips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    content TEXT,
    path TEXT,
    ts TEXT NOT NULL,
    favorite INTEGER NOT NULL DEFAULT 0,
    hash TEXT UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_ts ON clips (ts DESC);
CREATE INDEX IF NOT EXISTS idx_type ON clips (type);
CREATE INDEX IF NOT EXISTS idx_fav ON clips (favorite);
"""

class DB:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.conn.executescript(SCHEMA)

    def add_clip(self, type_: str, content: str, path: Optional[str], ts: str, favorite: bool, hash_: str) -> Optional[int]:
        try:
            cur = self.conn.execute(
                'INSERT INTO clips (type, content, path, ts, favorite, hash) VALUES (?, ?, ?, ?, ?, ?)',
                (type_, content, path, ts, int(favorite), hash_)
            )
            self.conn.commit()
            self.prune()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            self.conn.execute('UPDATE clips SET ts=? WHERE hash=?', (ts, hash_))
            self.conn.commit()
            return None

    def list_clips(self):
        rows = self.conn.execute('SELECT id, type, content, path, ts, favorite, hash FROM clips ORDER BY favorite DESC, ts DESC').fetchall()
        return [ClipItem(*row) for row in rows]

    def recent(self, limit: int = 10):
        rows = self.conn.execute('SELECT id, type, content, path, ts, favorite, hash FROM clips ORDER BY favorite DESC, ts DESC LIMIT ?', (limit,)).fetchall()
        return [ClipItem(*row) for row in rows]

    def delete(self, id_: int):
        self.conn.execute('DELETE FROM clips WHERE id=?', (id_,))
        self.conn.commit()

    def toggle_favorite(self, id_: int, value: Optional[bool] = None) -> bool:
        cur = self.conn.execute('SELECT favorite FROM clips WHERE id=?', (id_,)).fetchone()
        if not cur:
            return False
        current = bool(cur[0])
        new_val = int(not current) if value is None else int(value)
        self.conn.execute('UPDATE clips SET favorite=? WHERE id=?', (new_val, id_,))
        self.conn.commit()
        return bool(new_val)

    def prune(self):
        self.conn.execute('DELETE FROM clips WHERE id IN (SELECT id FROM clips WHERE favorite=0 ORDER BY ts DESC LIMIT -1 OFFSET ?)', (MAX_ITEMS,))
        self.conn.commit()

    def clear(self, keep_favorites: bool = True):
        if keep_favorites:
            self.conn.execute('DELETE FROM clips WHERE favorite=0')
        else:
            self.conn.execute('DELETE FROM clips')
        self.conn.commit()
