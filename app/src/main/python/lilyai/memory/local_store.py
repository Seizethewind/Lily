"""Local SQLite storage: approved memory, conversation history and settings are separate tables (notes section 9)."""
import re
import sqlite3
import threading
import time
import hashlib

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY, kind TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL,
    status TEXT NOT NULL, created REAL NOT NULL, updated REAL NOT NULL,
    UNIQUE (kind, content_hash)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT NOT NULL,
    role TEXT NOT NULL, content TEXT NOT NULL, ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def content_hash(text):
    normalized = re.sub(r"\s+", " ", text.strip()).casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class LocalStore:
    def __init__(self, path=":memory:"):
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._db.executescript(_SCHEMA)
            self._db.commit()

    def execute(self, sql, params=()):
        with self._lock:
            cur = self._db.execute(sql, params)
            self._db.commit()
            return cur.rowcount

    def query(self, sql, params=()):
        with self._lock:
            return [dict(r) for r in self._db.execute(sql, params)]

    def add_message(self, conversation_id, role, content):
        self.execute("INSERT INTO messages (conversation_id, role, content, ts) VALUES (?,?,?,?)",
                     (conversation_id, role, content, time.time()))

    def recent_messages(self, conversation_id, limit=50):
        rows = self.query("SELECT role, content, ts FROM messages WHERE conversation_id = ?"
                          " ORDER BY id DESC LIMIT ?", (conversation_id, limit))
        return list(reversed(rows))

    def set_setting(self, key, value):
        self.execute("INSERT INTO settings (key, value) VALUES (?, ?)"
                     " ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, str(value)))

    def get_setting(self, key, default=None):
        rows = self.query("SELECT value FROM settings WHERE key = ?", (key,))
        return rows[0]["value"] if rows else default

    def close(self):
        with self._lock:
            self._db.close()
