"""ChainArchive — Tier 3 hash-chained document archive."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ._utils import read_json, sha256_hex, write_json, now_iso, estimate_tokens
from .document import CombDocument, TemporalLinks


class ChainArchive:
    """Hash-chained document archive (Tier 3).

    Each document is stored as ``<root>/archive/<YYYY-MM-DD>.json`` and
    contains a SHA-256 hash of its content plus the previous document's
    hash, forming a tamper-evident chain analogous to a blockchain.
    """

    def __init__(self, root: Path) -> None:
        self._dir = root / "archive"
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _path(self, date: str) -> Path:
        return self._dir / f"{date}.json"

    def _compute_hash(self, content: str, prev_hash: Optional[str]) -> str:
        """Compute the chain hash for a document."""
        payload = (prev_hash or "") + content
        return sha256_hex(payload)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dates(self) -> list[str]:
        """Return all archived dates in chronological order."""
        return sorted(p.stem for p in self._dir.glob("*.json"))

    def get(self, date: str) -> Optional[CombDocument]:
        """Retrieve a document by date.

        Args:
            date: The date string (YYYY-MM-DD).

        Returns:
            The :class:`CombDocument`, or ``None`` if not found.
        """
        path = self._path(date)
        if not path.exists():
            return None
        return CombDocument.from_dict(read_json(path))

    def all(self) -> dict[str, CombDocument]:
        """Load all archived documents keyed by date."""
        docs: dict[str, CombDocument] = {}
        for date in self.dates():
            doc = self.get(date)
            if doc:
                docs[date] = doc
        return docs

    def latest(self) -> Optional[CombDocument]:
        """Return the most recent archived document."""
        dates = self.dates()
        return self.get(dates[-1]) if dates else None

    def put(
        self,
        date: str,
        content: str,
        *,
        metadata: Optional[dict[str, Any]] = None,
    ) -> CombDocument:
        """Archive a document, extending the hash chain.

        If a document for this date already exists, it is replaced and
        the chain is recomputed from that point forward.

        Args:
            date: The date string (YYYY-MM-DD).
            content: The full document text.
            metadata: Optional metadata dict.

        Returns:
            The newly created :class:`CombDocument`.
        """
        dates = self.dates()

        # Find previous document
        prev_doc: Optional[CombDocument] = None
        prev_hash: Optional[str] = None
        for d in reversed(dates):
            if d < date:
                prev_doc = self.get(d)
                if prev_doc:
                    prev_hash = prev_doc.hash
                break

        doc_hash = self._compute_hash(content, prev_hash)
        byte_size = len(content.encode("utf-8"))

        meta = {
            "byte_size": byte_size,
            "total_tokens": estimate_tokens(content),
            "created_at": now_iso(),
            **(metadata or {}),
        }

        doc = CombDocument(
            date=date,
            content=content,
            hash=doc_hash,
            prev_hash=prev_hash,
            metadata=meta,
            temporal=TemporalLinks(
                prev=prev_doc.date if prev_doc else None,
                next=None,
            ),
        )

        write_json(self._path(date), doc.to_dict())

        # Update previous document's next pointer
        if prev_doc and prev_doc.temporal.next != date:
            prev_doc.temporal.next = date
            write_json(self._path(prev_doc.date), prev_doc.to_dict())

        # Update next document's prev pointer and re-chain if needed
        for d in dates:
            if d > date:
                next_doc = self.get(d)
                if next_doc:
                    next_doc.prev_hash = doc_hash
                    next_doc.hash = self._compute_hash(next_doc.content, doc_hash)
                    next_doc.temporal.prev = date
                    if doc.temporal.next is None:
                        doc.temporal.next = d
                        write_json(self._path(date), doc.to_dict())
                    write_json(self._path(d), next_doc.to_dict())
                break

        return doc

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire hash chain.

        Returns:
            ``True`` if the chain is intact, ``False`` otherwise.
        """
        dates = self.dates()
        prev_hash: Optional[str] = None
        for date in dates:
            doc = self.get(date)
            if doc is None:
                return False
            expected = self._compute_hash(doc.content, prev_hash)
            if doc.hash != expected:
                return False
            if doc.prev_hash != prev_hash:
                return False
            prev_hash = doc.hash
        return True

    def count(self) -> int:
        """Return the number of archived documents."""
        return len(self.dates())
