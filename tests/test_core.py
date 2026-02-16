"""Tests for CombStore (core)."""

import shutil
import tempfile
from pathlib import Path

import pytest

from comb import CombStore


@pytest.fixture
def store(tmp_path):
    return CombStore(tmp_path / "test-store")


def test_stage_and_rollup(store):
    store.stage("Hello world", date="2026-01-01")
    store.stage("Second entry", date="2026-01-01")
    doc = store.rollup(date="2026-01-01")
    assert doc is not None
    assert doc.date == "2026-01-01"
    assert "Hello world" in doc.content
    assert "Second entry" in doc.content
    assert doc.hash
    assert doc.metadata["compaction_count"] == 2


def test_rollup_empty(store):
    assert store.rollup(date="2026-01-01") is None


def test_search(store):
    store.stage("The quick brown fox jumps over the lazy dog", date="2026-01-01")
    store.rollup(date="2026-01-01")
    store.stage("Python is a great programming language", date="2026-01-02")
    store.rollup(date="2026-01-02")

    results = store.search("fox")
    assert len(results) >= 1
    assert results[0].date == "2026-01-01"


def test_chain_integrity(store):
    for i in range(1, 4):
        store.stage(f"Day {i} content", date=f"2026-01-0{i}")
        store.rollup(date=f"2026-01-0{i}")

    assert store.verify_chain() is True


def test_walk_temporal(store):
    for i in range(1, 4):
        store.stage(f"Day {i}", date=f"2026-01-0{i}")
        store.rollup(date=f"2026-01-0{i}")

    docs = list(store.walk("2026-01-01", direction="temporal"))
    assert len(docs) == 3
    assert [d.date for d in docs] == ["2026-01-01", "2026-01-02", "2026-01-03"]


def test_get(store):
    store.stage("Test", date="2026-01-15")
    store.rollup(date="2026-01-15")
    doc = store.get("2026-01-15")
    assert doc is not None
    assert doc.date == "2026-01-15"
    assert store.get("2026-12-31") is None


def test_stats(store):
    store.stage("Content", date="2026-01-01")
    store.rollup(date="2026-01-01")
    s = store.stats()
    assert s["document_count"] == 1
    assert s["chain_valid"] is True


def test_semantic_walk(store):
    store.stage("Machine learning and neural networks are fascinating", date="2026-01-01")
    store.rollup(date="2026-01-01")
    store.stage("Deep learning neural networks for image recognition", date="2026-01-02")
    store.rollup(date="2026-01-02")
    store.stage("Cooking pasta with tomato sauce recipe", date="2026-01-03")
    store.rollup(date="2026-01-03")

    docs = list(store.walk("2026-01-01", direction="semantic", depth=3))
    assert len(docs) >= 1
