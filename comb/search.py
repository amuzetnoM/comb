"""SearchBackend protocol + built-in BM25 implementation."""

from __future__ import annotations

import math
from typing import Protocol, runtime_checkable

from ._utils import tokenize


@runtime_checkable
class SearchBackend(Protocol):
    """Protocol that any search backend must satisfy.

    Implement this to plug in HEKTOR or any other engine.
    """

    def index(self, doc_id: str, text: str) -> None:
        """Index a document.

        Args:
            doc_id: Unique document identifier (typically a date string).
            text: The document text to index.
        """
        ...

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        """Search indexed documents.

        Args:
            query: The search query.
            k: Maximum number of results to return.

        Returns:
            List of ``(doc_id, score)`` tuples sorted by descending score.
        """
        ...


class BM25Search:
    """A pure-Python BM25 search implementation with zero dependencies.

    Good enough for hundreds or even thousands of documents.
    For larger corpora, plug in HEKTOR via the :class:`SearchBackend` protocol.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._docs: dict[str, list[str]] = {}  # doc_id -> tokens
        self._doc_len: dict[str, int] = {}
        self._avgdl: float = 0.0
        self._df: dict[str, int] = {}  # term -> doc frequency
        self._n: int = 0

    def index(self, doc_id: str, text: str) -> None:
        """Index a document for BM25 retrieval.

        Args:
            doc_id: Unique document identifier.
            text: The document text.
        """
        tokens = tokenize(text)
        # If re-indexing, remove old stats
        if doc_id in self._docs:
            old = set(self._docs[doc_id])
            for t in old:
                self._df[t] = max(0, self._df.get(t, 1) - 1)
            self._n -= 1

        self._docs[doc_id] = tokens
        self._doc_len[doc_id] = len(tokens)
        self._n += 1

        seen: set[str] = set()
        for t in tokens:
            if t not in seen:
                self._df[t] = self._df.get(t, 0) + 1
                seen.add(t)

        total = sum(self._doc_len.values())
        self._avgdl = total / self._n if self._n else 0.0

    def remove(self, doc_id: str) -> None:
        """Remove a document from the index.

        Args:
            doc_id: The document to remove.
        """
        if doc_id not in self._docs:
            return
        old = set(self._docs[doc_id])
        for t in old:
            self._df[t] = max(0, self._df.get(t, 1) - 1)
        del self._docs[doc_id]
        del self._doc_len[doc_id]
        self._n -= 1
        total = sum(self._doc_len.values())
        self._avgdl = total / self._n if self._n else 0.0

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        """Search the index using BM25 scoring.

        Args:
            query: The search query.
            k: Maximum results to return.

        Returns:
            List of ``(doc_id, score)`` tuples, descending by score.
        """
        qtokens = tokenize(query)
        if not qtokens or not self._docs:
            return []

        scores: dict[str, float] = {}
        for doc_id, tokens in self._docs.items():
            score = 0.0
            dl = self._doc_len[doc_id]
            tf_map: dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for qt in qtokens:
                if qt not in tf_map:
                    continue
                tf = tf_map[qt]
                df = self._df.get(qt, 0)
                idf = math.log((self._n - df + 0.5) / (df + 0.5) + 1.0)
                num = tf * (self._k1 + 1)
                den = tf + self._k1 * (1 - self._b + self._b * dl / self._avgdl)
                score += idf * num / den

            if score > 0:
                scores[doc_id] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:k]
