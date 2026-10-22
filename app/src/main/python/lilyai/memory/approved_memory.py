"""Memory proposals need explicit owner approval before they become persistent knowledge (notes section 9)."""
import time
import uuid

from .local_store import LocalStore, content_hash

KINDS = ("preference", "fact", "procedure")
PROPOSED, APPROVED, REJECTED = "proposed", "approved", "rejected"


class MemoryProposalError(Exception):
    pass


class MemoryManager:
    def __init__(self, store: LocalStore):
        self._store = store

    def propose(self, kind, content):
        """Returns (memory_id, created). A duplicate returns the existing id and never changes its status."""
        if kind not in KINDS:
            raise MemoryProposalError(f"unknown memory kind: {kind}")
        if not content or not content.strip():
            raise MemoryProposalError("memory content is empty")
        digest = content_hash(content)
        existing = self._store.query("SELECT id FROM memories WHERE kind = ? AND content_hash = ?", (kind, digest))
        if existing:
            return existing[0]["id"], False
        memory_id, now = uuid.uuid4().hex, time.time()
        self._store.execute(
            "INSERT INTO memories (id, kind, content, content_hash, status, created, updated) VALUES (?,?,?,?,?,?,?)",
            (memory_id, kind, content.strip(), digest, PROPOSED, now, now))
        return memory_id, True

    def _resolve(self, memory_id, new_status):
        changed = self._store.execute(
            "UPDATE memories SET status = ?, updated = ? WHERE id = ? AND status = ?",
            (new_status, time.time(), memory_id, PROPOSED))
        if not changed:
            raise MemoryProposalError("only a proposed memory can be approved or rejected")

    def approve(self, memory_id):
        self._resolve(memory_id, APPROVED)

    def reject(self, memory_id):
        self._resolve(memory_id, REJECTED)

    def list(self, status, kind=None):
        sql, params = "SELECT id, kind, content, status FROM memories WHERE status = ?", [status]
        if kind:
            sql, params = sql + " AND kind = ?", params + [kind]
        return self._store.query(sql + " ORDER BY created", params)

    def sync_candidates(self):
        """Only approved memories are ever eligible for cloud synchronization."""
        return self.list(APPROVED)
