"""CombStore — the main entry point for COMB."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Literal, Optional, Union

from .archive import ChainArchive
from .document import CombDocument
from .honeycomb import HoneycombGraph
from .search import BM25Search, SearchBackend
from .staging import DailyStaging
from ._utils import today_str


class CombStore:
    """Chain-Ordered Memory Base — honeycomb-structured lossless context archival.

    A CombStore manages three tiers of storage:

    - **Tier 1 (Active)** — the agent's current context window (not managed here).
    - **Tier 2 (Daily Staging)** — append-only staging for today's conversations.
    - **Tier 3 (Chain Archive)** — hash-chained, honeycomb-linked document archive.

    Args:
        path: Directory where all COMB data is stored.  Created if it
            doesn't exist.
        search_backend: An optional :class:`SearchBackend` implementation.
            Defaults to the built-in BM25 engine.

    Example::

        store = CombStore("./my-memory")
        store.stage("Hello world", metadata={"session": "demo"})
        store.rollup()
        results = store.search("hello")
    """

    def __init__(
        self,
        path: Union[str, Path],
        *,
        search_backend: Optional[SearchBackend] = None,
    ) -> None:
        self._root = Path(path)
        self._root.mkdir(parents=True, exist_ok=True)

        self._staging = DailyStaging(self._root)
        self._archive = ChainArchive(self._root)
        self._graph = HoneycombGraph()

        self._search: SearchBackend = search_backend or BM25Search()

        # Build search index from existing archive
        for date in self._archive.dates():
            doc = self._archive.get(date)
            if doc:
                self._search.index(doc.date, doc.content)

    # ------------------------------------------------------------------
    # Tier 2: Staging
    # ------------------------------------------------------------------

    def stage(
        self,
        text: str,
        *,
        metadata: Optional[dict[str, Any]] = None,
        date: Optional[str] = None,
    ) -> None:
        """Stage a conversation dump (Tier 2).

        Appends the text to today's staging file.  Call :meth:`rollup`
        to promote staged data to the archive.

        Args:
            text: Raw conversation text.
            metadata: Arbitrary metadata to attach.
            date: Override the staging date (default: today UTC).
        """
        self._staging.append(text, date=date, metadata=metadata)

    # ------------------------------------------------------------------
    # Tier 2 → Tier 3: Rollup
    # ------------------------------------------------------------------

    def rollup(self, date: Optional[str] = None) -> Optional[CombDocument]:
        """Roll up staged data into the chain archive (Tier 2 → Tier 3).

        Concatenates all staged entries for the given date, archives them
        as a single hash-chained document, computes honeycomb links, and
        clears the staging file.

        Args:
            date: The date to roll up (default: today UTC).

        Returns:
            The newly archived :class:`CombDocument`, or ``None`` if
            nothing was staged.
        """
        date = date or today_str()
        content = self._staging.concatenate(date)
        if content is None:
            return None

        # Count staged entries for metadata
        entries = self._staging.read(date)
        meta = {"compaction_count": len(entries)}

        # Archive
        doc = self._archive.put(date, content, metadata=meta)

        # Compute honeycomb links
        all_docs = self._archive.all()
        doc.semantic = self._graph.compute_semantic_links(doc, all_docs)
        doc.social = self._graph.compute_social_links(doc, all_docs)

        # Persist updated links
        from ._utils import write_json

        write_json(self._root / "archive" / f"{date}.json", doc.to_dict())

        # Index for search
        self._search.index(doc.date, doc.content)

        # Clear staging
        self._staging.clear(date)

        return doc

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        mode: Literal["bm25", "semantic", "hybrid"] = "bm25",
        k: int = 5,
    ) -> list[CombDocument]:
        """Search the archive.

        Args:
            query: The search query.
            mode: Search mode.  Currently only ``"bm25"`` is implemented
                in the built-in backend.  Pass a custom
                :class:`SearchBackend` for semantic/hybrid.
            k: Maximum number of results.

        Returns:
            List of :class:`CombDocument` instances with
            ``similarity_score`` set, sorted by relevance.
        """
        results = self._search.search(query, k=k)
        docs: list[CombDocument] = []
        for doc_id, score in results:
            doc = self._archive.get(doc_id)
            if doc:
                doc.similarity_score = score
                docs.append(doc)
        return docs

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def get(self, date: str) -> Optional[CombDocument]:
        """Retrieve an archived document by date.

        Args:
            date: The date string (YYYY-MM-DD).

        Returns:
            The :class:`CombDocument`, or ``None`` if not found.
        """
        return self._archive.get(date)

    def walk(
        self,
        start: str,
        *,
        direction: Literal["temporal", "semantic"] = "temporal",
        depth: int = 100,
    ) -> Iterator[CombDocument]:
        """Walk the honeycomb graph from a starting document.

        Args:
            start: Starting date.
            direction: ``"temporal"`` follows the prev/next chain forward;
                ``"semantic"`` follows semantic neighbors breadth-first.
            depth: Maximum number of documents to yield.

        Yields:
            :class:`CombDocument` instances along the walk path.
        """
        if direction == "temporal":
            yield from self._walk_temporal(start, depth)
        elif direction == "semantic":
            yield from self._walk_semantic(start, depth)

    def _walk_temporal(self, start: str, depth: int) -> Iterator[CombDocument]:
        current = self._archive.get(start)
        count = 0
        while current and count < depth:
            yield current
            count += 1
            next_date = current.temporal.next
            if next_date is None:
                break
            current = self._archive.get(next_date)

    def _walk_semantic(self, start: str, depth: int) -> Iterator[CombDocument]:
        visited: set[str] = set()
        queue: list[str] = [start]
        count = 0
        while queue and count < depth:
            date = queue.pop(0)
            if date in visited:
                continue
            visited.add(date)
            doc = self._archive.get(date)
            if doc is None:
                continue
            yield doc
            count += 1
            for neighbor in doc.semantic.neighbors:
                if neighbor.target not in visited:
                    queue.append(neighbor.target)

    # ------------------------------------------------------------------
    # Chain integrity
    # ------------------------------------------------------------------

    def verify_chain(self) -> bool:
        """Verify the integrity of the hash chain.

        Returns:
            ``True`` if no tampering detected, ``False`` otherwise.
        """
        return self._archive.verify_chain()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return statistics about the store.

        Returns:
            Dict with document count, total size, chain length, link counts,
            and staging info.
        """
        all_docs = self._archive.all()
        total_bytes = sum(d.metadata.get("byte_size", 0) for d in all_docs.values())
        total_semantic = sum(len(d.semantic.neighbors) for d in all_docs.values())
        total_social = sum(len(d.social.links) for d in all_docs.values())

        return {
            "document_count": len(all_docs),
            "total_bytes": total_bytes,
            "chain_length": self._archive.count(),
            "semantic_links": total_semantic,
            "social_links": total_social,
            "staged_dates": self._staging.dates(),
            "chain_valid": self._archive.verify_chain(),
        }
