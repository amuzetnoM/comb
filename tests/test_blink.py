"""Tests for the blink/recall pattern."""

import pytest
from comb import CombStore


@pytest.fixture
def store(tmp_path):
    return CombStore(str(tmp_path / "test-store"))


class TestRecall:
    def test_recall_empty(self, store):
        assert store.recall() == "(empty memory)"

    def test_recall_includes_staged(self, store):
        store.stage("session context alpha")
        text = store.recall()
        assert "session context alpha" in text
        assert "[staged" in text

    def test_recall_includes_archived(self, store):
        store.stage("archived context beta")
        store.rollup()
        text = store.recall()
        assert "archived context beta" in text
        assert "[archive" in text

    def test_recall_staged_before_archived(self, store):
        store.stage("old stuff", date="2026-01-01")
        store.rollup(date="2026-01-01")
        store.stage("fresh stuff")
        text = store.recall()
        # Staged (fresh) should appear before archived (old)
        staged_pos = text.find("fresh stuff")
        archived_pos = text.find("old stuff")
        assert staged_pos < archived_pos

    def test_recall_no_staged(self, store):
        store.stage("only staged")
        text = store.recall(include_staged=False)
        assert "only staged" not in text

    def test_recall_k_limits(self, store):
        for i in range(10):
            store.stage(f"doc {i}", date=f"2026-01-{i+1:02d}")
            store.rollup(date=f"2026-01-{i+1:02d}")
        text = store.recall(k=3)
        assert "doc 9" in text
        assert "doc 7" in text
        assert "doc 0" not in text


class TestBlink:
    def test_blink_stages_and_returns_recall(self, store):
        result = store.blink("operational context gamma")
        assert "operational context gamma" in result

    def test_blink_with_rollup(self, store):
        store.blink("blink content", rollup=True)
        # After rollup, staged should be empty but archive should have it
        assert len(store._staging.dates()) == 0
        text = store.recall()
        assert "blink content" in text

    def test_blink_metadata_tagged(self, store):
        store.blink("tagged content")
        entries = store._staging.read()
        assert any(e["metadata"].get("blink") is True for e in entries)

    def test_blink_multiple_accumulate(self, store):
        store.blink("first flush")
        store.blink("second flush")
        text = store.recall()
        assert "first flush" in text
        assert "second flush" in text
