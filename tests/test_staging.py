"""Tests for DailyStaging."""

import pytest
from comb.staging import DailyStaging


@pytest.fixture
def staging(tmp_path):
    return DailyStaging(tmp_path)


def test_append_and_read(staging):
    staging.append("First entry", date="2026-01-01")
    staging.append("Second entry", date="2026-01-01")
    entries = staging.read("2026-01-01")
    assert len(entries) == 2
    assert entries[0]["text"] == "First entry"
    assert entries[1]["text"] == "Second entry"


def test_read_empty(staging):
    assert staging.read("2026-12-31") == []


def test_concatenate(staging):
    staging.append("A", date="2026-01-01")
    staging.append("B", date="2026-01-01")
    result = staging.concatenate("2026-01-01")
    assert result == "A\n\nB"


def test_concatenate_empty(staging):
    assert staging.concatenate("2026-01-01") is None


def test_clear(staging):
    staging.append("Data", date="2026-01-01")
    staging.clear("2026-01-01")
    assert staging.read("2026-01-01") == []


def test_dates(staging):
    staging.append("A", date="2026-01-03")
    staging.append("B", date="2026-01-01")
    assert staging.dates() == ["2026-01-01", "2026-01-03"]


def test_metadata(staging):
    staging.append("Text", date="2026-01-01", metadata={"session": "abc"})
    entries = staging.read("2026-01-01")
    assert entries[0]["metadata"]["session"] == "abc"
