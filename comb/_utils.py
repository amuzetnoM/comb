"""Internal utilities for COMB — hashing, serialization, time helpers."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_hex(data: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def today_str() -> str:
    """Return today's date as YYYY-MM-DD (UTC)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_json(path: Path) -> Any:
    """Read and parse a JSON file."""
    return json.loads(path.read_text("utf-8"))


def write_json(path: Path, data: Any) -> None:
    """Write data to a JSON file (pretty-printed)."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", "utf-8")


def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for BM25."""
    return re.findall(r"[a-z0-9]+", text.lower())


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars per token)."""
    return max(1, len(text) // 4)


_POSITIVE_WORDS = frozenset(
    "thanks thank great good awesome excellent love appreciate happy glad "
    "wonderful nice agree yes perfect beautiful amazing helpful".split()
)
_NEGATIVE_WORDS = frozenset(
    "bad wrong hate disagree no never terrible awful frustrated angry "
    "annoying disappointed confused fail error broken".split()
)


def simple_sentiment(text: str) -> float:
    """Return a sentiment score in [-1.0, 1.0] based on keyword counting."""
    words = tokenize(text)
    if not words:
        return 0.0
    pos = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total
