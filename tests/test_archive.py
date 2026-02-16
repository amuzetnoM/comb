"""Tests for ChainArchive."""

import pytest
from comb.archive import ChainArchive


@pytest.fixture
def archive(tmp_path):
    return ChainArchive(tmp_path)


def test_put_and_get(archive):
    doc = archive.put("2026-01-01", "Hello world")
    assert doc.date == "2026-01-01"
    assert doc.hash
    assert doc.prev_hash is None

    retrieved = archive.get("2026-01-01")
    assert retrieved is not None
    assert retrieved.hash == doc.hash


def test_chain(archive):
    d1 = archive.put("2026-01-01", "Day one")
    d2 = archive.put("2026-01-02", "Day two")
    assert d2.prev_hash == d1.hash
    assert d2.temporal.prev == "2026-01-01"

    d1_updated = archive.get("2026-01-01")
    assert d1_updated.temporal.next == "2026-01-02"


def test_verify_chain(archive):
    archive.put("2026-01-01", "A")
    archive.put("2026-01-02", "B")
    archive.put("2026-01-03", "C")
    assert archive.verify_chain() is True


def test_dates(archive):
    archive.put("2026-01-03", "C")
    archive.put("2026-01-01", "A")
    assert archive.dates() == ["2026-01-01", "2026-01-03"]


def test_count(archive):
    assert archive.count() == 0
    archive.put("2026-01-01", "A")
    assert archive.count() == 1


def test_latest(archive):
    assert archive.latest() is None
    archive.put("2026-01-01", "A")
    archive.put("2026-01-05", "B")
    assert archive.latest().date == "2026-01-05"


def test_get_nonexistent(archive):
    assert archive.get("2099-01-01") is None
