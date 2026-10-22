"""Local task timeline, separate from chat messages (notes section 12)."""
import sqlite3
import threading
import time

from ..utils.logging_utils import redact

_SCHEMA = """
CREATE TABLE IF NOT EXISTS task_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    ts REAL NOT NULL,
    event_type TEXT NOT NULL,
    state TEXT, tool TEXT, approval TEXT, summary TEXT,
    error_category TEXT, error_message TEXT, cancellation_state TEXT
)"""


class TaskLog:
    def __init__(self, path=":memory:", secrets=()):
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._secrets = tuple(secrets)
        with self._lock:
            self._db.execute(_SCHEMA)
            self._db.commit()

    def record(self, task_id, event_type, *, state=None, tool=None, approval=None, summary=None,
               error_category=None, error_message=None, cancellation_state=None):
        summary = redact(summary, self._secrets)
        error_message = redact(error_message, self._secrets)
        with self._lock:
            cur = self._db.execute(
                "INSERT INTO task_events (task_id, ts, event_type, state, tool, approval, summary,"
                " error_category, error_message, cancellation_state) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (task_id, time.time(), event_type, state, tool, approval, summary,
                 error_category, error_message, cancellation_state))
            self._db.commit()
            return cur.lastrowid

    def events(self, task_id=None):
        sql, params = "SELECT * FROM task_events", ()
        if task_id is not None:
            sql, params = sql + " WHERE task_id = ?", (task_id,)
        with self._lock:
            return [dict(r) for r in self._db.execute(sql + " ORDER BY event_id", params)]

    def close(self):
        with self._lock:
            self._db.close()
