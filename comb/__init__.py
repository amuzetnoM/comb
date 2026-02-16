"""COMB — Chain-Ordered Memory Base.

Honeycomb-structured, lossless context archival for AI agents.

Usage::

    from comb import CombStore

    store = CombStore("./my-memory")
    store.stage("conversation text here")
    store.rollup()
    results = store.search("query")
"""

from .core import CombStore
from .document import (
    CombDocument,
    SemanticLinks,
    SemanticNeighbor,
    SocialLink,
    SocialLinks,
    TemporalLinks,
)
from .search import BM25Search, SearchBackend
from .staging import DailyStaging
from .archive import ChainArchive
from .honeycomb import HoneycombGraph

__version__ = "0.1.0"

__all__ = [
    "CombStore",
    "CombDocument",
    "TemporalLinks",
    "SemanticLinks",
    "SemanticNeighbor",
    "SocialLink",
    "SocialLinks",
    "BM25Search",
    "SearchBackend",
    "DailyStaging",
    "ChainArchive",
    "HoneycombGraph",
    "__version__",
]
