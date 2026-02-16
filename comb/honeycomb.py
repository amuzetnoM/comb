"""HoneycombGraph — three-directional link management."""

from __future__ import annotations

import re
from typing import Any, Optional

from ._utils import tokenize, simple_sentiment
from .document import (
    CombDocument,
    SemanticLinks,
    SemanticNeighbor,
    SocialLink,
    SocialLinks,
)


def _term_freq_vector(text: str) -> dict[str, int]:
    """Build a term-frequency vector from text."""
    vec: dict[str, int] = {}
    for t in tokenize(text):
        vec[t] = vec.get(t, 0) + 1
    return vec


def _cosine_similarity(a: dict[str, int], b: dict[str, int]) -> float:
    """Compute cosine similarity between two term-frequency vectors."""
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    mag_a = sum(v * v for v in a.values()) ** 0.5
    mag_b = sum(v * v for v in b.values()) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _parse_turns(text: str) -> list[dict[str, str]]:
    """Parse conversation turns from text with role markers like [user], [assistant]."""
    pattern = re.compile(r"\[(user|assistant|system)\]\s*", re.IGNORECASE)
    turns: list[dict[str, str]] = []
    parts = pattern.split(text)
    # parts: [pre, role1, content1, role2, content2, ...]
    i = 1
    while i < len(parts) - 1:
        role = parts[i].lower()
        content = parts[i + 1].strip()
        if content:
            turns.append({"role": role, "content": content})
        i += 2
    return turns


def _compute_social_delta(text_a: str, text_b: str) -> float:
    """Compute a simple social/relationship delta between two documents.

    Positive = strengthening (inward), negative = cooling (outward).
    Based on engagement ratio and sentiment.
    """
    turns_a = _parse_turns(text_a)
    turns_b = _parse_turns(text_b)

    def engagement(turns: list[dict[str, str]]) -> float:
        if not turns:
            return 0.0
        lengths = [len(t["content"]) for t in turns]
        return sum(lengths) / len(lengths) if lengths else 0.0

    eng_a = engagement(turns_a)
    eng_b = engagement(turns_b)

    # Engagement delta: higher engagement in b vs a = warming
    if eng_a + eng_b == 0:
        eng_delta = 0.0
    else:
        eng_delta = (eng_b - eng_a) / (eng_a + eng_b)

    # Sentiment component
    sent_a = simple_sentiment(text_a)
    sent_b = simple_sentiment(text_b)
    sent_delta = (sent_b - sent_a) / 2.0

    # Combined, clamped to [-1, 1]
    raw = eng_delta * 0.6 + sent_delta * 0.4
    return max(-1.0, min(1.0, raw))


class HoneycombGraph:
    """Manages the three-directional link structure of the COMB archive.

    Computes and maintains:
    - **Temporal** links (prev/next chain) — set during archive insertion
    - **Semantic** links — cosine similarity over term-frequency vectors
    - **Social** links — relationship gradient based on engagement and sentiment
    """

    def __init__(self, max_semantic: int = 5, max_social: int = 5) -> None:
        self._max_semantic = max_semantic
        self._max_social = max_social

    def compute_semantic_links(
        self,
        doc: CombDocument,
        archive: dict[str, CombDocument],
    ) -> SemanticLinks:
        """Compute semantic neighbors for a document against the archive.

        Args:
            doc: The document to compute links for.
            archive: All archived documents keyed by date.

        Returns:
            A :class:`SemanticLinks` instance with the top-k neighbors.
        """
        vec = _term_freq_vector(doc.content)
        scored: list[tuple[str, float]] = []
        for other_date, other_doc in archive.items():
            if other_date == doc.date:
                continue
            other_vec = _term_freq_vector(other_doc.content)
            sim = _cosine_similarity(vec, other_vec)
            if sim > 0.01:
                scored.append((other_date, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        neighbors = [
            SemanticNeighbor(target=d, score=s)
            for d, s in scored[: self._max_semantic]
        ]
        return SemanticLinks(neighbors=neighbors)

    def compute_social_links(
        self,
        doc: CombDocument,
        archive: dict[str, CombDocument],
    ) -> SocialLinks:
        """Compute social / relationship-gradient links for a document.

        Args:
            doc: The document to compute links for.
            archive: All archived documents keyed by date.

        Returns:
            A :class:`SocialLinks` instance.
        """
        scored: list[tuple[str, float]] = []
        for other_date, other_doc in archive.items():
            if other_date == doc.date:
                continue
            delta = _compute_social_delta(other_doc.content, doc.content)
            if abs(delta) > 0.01:
                scored.append((other_date, delta))

        scored.sort(key=lambda x: abs(x[1]), reverse=True)
        links = [
            SocialLink(
                target=d,
                direction="inward" if delta > 0 else "outward",
                delta=delta,
            )
            for d, delta in scored[: self._max_social]
        ]
        return SocialLinks(links=links)
