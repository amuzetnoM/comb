"""Tests for BM25Search."""

import pytest
from comb.search import BM25Search


@pytest.fixture
def bm25():
    s = BM25Search()
    s.index("doc1", "The quick brown fox jumps over the lazy dog")
    s.index("doc2", "Python is a great programming language for data science")
    s.index("doc3", "The fox and the hound are friends")
    return s


def test_search_basic(bm25):
    results = bm25.search("fox")
    assert len(results) >= 1
    ids = [r[0] for r in results]
    assert "doc1" in ids


def test_search_ranking(bm25):
    results = bm25.search("python programming")
    assert results[0][0] == "doc2"


def test_search_no_results(bm25):
    results = bm25.search("xyz123nonexistent")
    assert results == []


def test_search_empty_query(bm25):
    assert BM25Search().search("anything") == []


def test_search_k_limit(bm25):
    results = bm25.search("the", k=1)
    assert len(results) == 1


def test_reindex(bm25):
    bm25.index("doc1", "Completely new content about cats")
    results = bm25.search("fox")
    ids = [r[0] for r in results]
    assert "doc1" not in ids or results[0][0] != "doc1"


def test_remove(bm25):
    bm25.remove("doc1")
    results = bm25.search("fox")
    ids = [r[0] for r in results]
    # doc1 should be gone, doc3 might still match
    assert "doc1" not in ids
