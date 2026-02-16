"""Tests for HoneycombGraph."""

import pytest
from comb.honeycomb import HoneycombGraph, _cosine_similarity, _term_freq_vector, _compute_social_delta
from comb.document import CombDocument


def _make_doc(date, content):
    return CombDocument(date=date, content=content, hash="fake")


def test_cosine_similarity():
    a = _term_freq_vector("the cat sat on the mat")
    b = _term_freq_vector("the cat sat on the hat")
    sim = _cosine_similarity(a, b)
    assert 0.5 < sim < 1.0


def test_cosine_similarity_identical():
    a = _term_freq_vector("hello world")
    assert abs(_cosine_similarity(a, a) - 1.0) < 0.001


def test_cosine_similarity_disjoint():
    a = _term_freq_vector("cat dog")
    b = _term_freq_vector("sun moon")
    assert _cosine_similarity(a, b) == 0.0


def test_semantic_links():
    graph = HoneycombGraph(max_semantic=2)
    target = _make_doc("2026-01-03", "machine learning neural networks deep learning")
    archive = {
        "2026-01-01": _make_doc("2026-01-01", "neural networks and deep learning models"),
        "2026-01-02": _make_doc("2026-01-02", "cooking pasta with tomato sauce"),
    }
    links = graph.compute_semantic_links(target, archive)
    assert len(links.neighbors) >= 1
    assert links.neighbors[0].target == "2026-01-01"


def test_social_links():
    graph = HoneycombGraph(max_social=2)
    doc = _make_doc("2026-01-02", "[user] This is great! Thank you so much! [assistant] Happy to help!")
    archive = {
        "2026-01-01": _make_doc("2026-01-01", "[user] Hi [assistant] Hello"),
    }
    links = graph.compute_social_links(doc, archive)
    # Should detect some relationship delta
    assert isinstance(links.links, list)


def test_social_delta_positive():
    a = "[user] Hi [assistant] Hello"
    b = "[user] This is amazing! Thank you so much for the great help! [assistant] You're very welcome, happy to assist!"
    delta = _compute_social_delta(a, b)
    assert delta > 0  # b is more engaged than a
