"""CombDocument — represents a single archived document in the chain."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Link containers — lightweight accessors for the three honeycomb directions
# ---------------------------------------------------------------------------

@dataclass
class TemporalLinks:
    """Previous/next pointers in the chronological chain."""

    prev: Optional[str] = None
    next: Optional[str] = None

    def to_dict(self) -> dict[str, Optional[str]]:
        return {"prev": self.prev, "next": self.next}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TemporalLinks":
        return cls(prev=d.get("prev"), next=d.get("next"))


@dataclass
class SemanticNeighbor:
    """A single semantic link to another document."""

    target: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {"target": self.target, "score": round(self.score, 4)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SemanticNeighbor":
        return cls(target=d["target"], score=d["score"])


@dataclass
class SocialLink:
    """A single social / relationship-gradient link."""

    target: str
    direction: str  # "inward" | "outward"
    delta: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "direction": self.direction,
            "delta": round(self.delta, 4),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SocialLink":
        return cls(target=d["target"], direction=d["direction"], delta=d["delta"])


@dataclass
class SemanticLinks:
    """Accessor for semantic neighbors."""

    neighbors: list[SemanticNeighbor] = field(default_factory=list)

    def to_list(self) -> list[dict[str, Any]]:
        return [n.to_dict() for n in self.neighbors]

    @classmethod
    def from_list(cls, items: list[dict[str, Any]]) -> "SemanticLinks":
        return cls(neighbors=[SemanticNeighbor.from_dict(i) for i in items])


@dataclass
class SocialLinks:
    """Accessor for social / relationship-gradient links."""

    links: list[SocialLink] = field(default_factory=list)

    @property
    def strengthened(self) -> list[SocialLink]:
        """Links where the relationship deepened (inward fade)."""
        return [l for l in self.links if l.delta > 0]

    @property
    def cooled(self) -> list[SocialLink]:
        """Links where the relationship cooled (outward fade)."""
        return [l for l in self.links if l.delta < 0]

    def to_list(self) -> list[dict[str, Any]]:
        return [l.to_dict() for l in self.links]

    @classmethod
    def from_list(cls, items: list[dict[str, Any]]) -> "SocialLinks":
        return cls(links=[SocialLink.from_dict(i) for i in items])


# ---------------------------------------------------------------------------
# CombDocument
# ---------------------------------------------------------------------------

@dataclass
class CombDocument:
    """A single document in the COMB archive.

    Each document represents one day's rolled-up conversation content,
    hash-chained to its predecessor and linked in three directions:
    temporal, semantic, and social.
    """

    date: str
    content: str
    hash: str
    prev_hash: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    temporal: TemporalLinks = field(default_factory=TemporalLinks)
    semantic: SemanticLinks = field(default_factory=SemanticLinks)
    social: SocialLinks = field(default_factory=SocialLinks)

    # Transient — set during search/walk, not persisted
    similarity_score: Optional[float] = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "date": self.date,
            "content": self.content,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "metadata": self.metadata,
            "links": {
                "temporal": self.temporal.to_dict(),
                "semantic": self.semantic.to_list(),
                "social": self.social.to_list(),
            },
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CombDocument":
        """Deserialize from a dictionary."""
        links = d.get("links", {})
        return cls(
            date=d["date"],
            content=d["content"],
            hash=d["hash"],
            prev_hash=d.get("prev_hash"),
            metadata=d.get("metadata", {}),
            temporal=TemporalLinks.from_dict(links.get("temporal", {})),
            semantic=SemanticLinks.from_list(links.get("semantic", [])),
            social=SocialLinks.from_list(links.get("social", [])),
        )

    def to_json(self, **kwargs: Any) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, **kwargs)

    @classmethod
    def from_json(cls, raw: str) -> "CombDocument":
        """Deserialize from a JSON string."""
        return cls.from_dict(json.loads(raw))
