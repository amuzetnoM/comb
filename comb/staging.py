"""DailyStaging — Tier 2 append-only staging for today's conversations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from ._utils import now_iso, today_str, estimate_tokens


class DailyStaging:
    """Append-only staging area for the current day's conversation dumps.

    Each call to :meth:`append` adds a timestamped entry to today's staging
    file.  At rollup time the staged entries are concatenated into a single
    archive document and the staging file is removed.

    Staging files live at ``<root>/staging/<YYYY-MM-DD>.jsonl`` — one
    JSON object per line.
    """

    def __init__(self, root: Path) -> None:
        self._dir = root / "staging"
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(
        self,
        text: str,
        *,
        date: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Append a conversation dump to today's staging file.

        Args:
            text: The raw conversation text to stage.
            date: Override the staging date (default: today UTC).
            metadata: Arbitrary metadata to attach to this entry.
        """
        date = date or today_str()
        entry = {
            "timestamp": now_iso(),
            "text": text,
            "byte_size": len(text.encode("utf-8")),
            "est_tokens": estimate_tokens(text),
            "metadata": metadata or {},
        }
        path = self._dir / f"{date}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def read(self, date: Optional[str] = None) -> list[dict[str, Any]]:
        """Read all staged entries for a given date.

        Args:
            date: The date to read (default: today UTC).

        Returns:
            List of staged entry dicts, in append order.
        """
        date = date or today_str()
        path = self._dir / f"{date}.jsonl"
        if not path.exists():
            return []
        entries: list[dict[str, Any]] = []
        for line in path.read_text("utf-8").splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries

    def concatenate(self, date: Optional[str] = None) -> Optional[str]:
        """Concatenate all staged entries for a date into a single string.

        Args:
            date: The date to concatenate (default: today UTC).

        Returns:
            The concatenated text, or ``None`` if nothing was staged.
        """
        entries = self.read(date)
        if not entries:
            return None
        return "\n\n".join(e["text"] for e in entries)

    def clear(self, date: Optional[str] = None) -> None:
        """Remove the staging file for a given date.

        Args:
            date: The date to clear (default: today UTC).
        """
        date = date or today_str()
        path = self._dir / f"{date}.jsonl"
        if path.exists():
            path.unlink()

    def dates(self) -> list[str]:
        """Return sorted list of dates that have staged data."""
        return sorted(p.stem for p in self._dir.glob("*.jsonl"))
