# Architecture

## Overview

COMB (Chain-Ordered Memory Base) is a three-tier, file-based archival system for AI conversation history. It prioritizes lossless storage and navigability over compression.

## Three Tiers

### Tier 1: Active (not managed by COMB)
The agent's current context window. COMB doesn't touch this — it's the agent's responsibility.

### Tier 2: Daily Staging
An append-only JSONL file per day. Each call to `store.stage()` appends a timestamped entry. This is the accumulation buffer — conversations flow in throughout the day.

**Storage:** `<root>/staging/YYYY-MM-DD.jsonl`

### Tier 3: Chain Archive
One JSON document per day, created by `store.rollup()`. Each document contains:
- The concatenated text from all staged entries
- A SHA-256 hash of `prev_hash + content`
- Three-directional honeycomb links

**Storage:** `<root>/archive/YYYY-MM-DD.json`

## The Hash Chain

Documents are chained via SHA-256:

```
hash(doc) = SHA-256(prev_hash + content)
```

This creates a tamper-evident chain. If any document is modified, all subsequent hashes become invalid. Verify with `store.verify_chain()`.

## Honeycomb Links

### Temporal
Simple prev/next pointers forming a doubly-linked list in chronological order.

### Semantic
Cosine similarity over term-frequency vectors (bag of words). During rollup, the new document is compared against all existing documents, and the top-k most similar are linked.

The built-in implementation is intentionally simple — no TF-IDF weighting, no embeddings. For better semantic matching, plug in a custom `SearchBackend`.

### Social
Relationship gradient tracking based on:
1. **Engagement ratio** — average turn length comparison between documents
2. **Sentiment polarity** — simple keyword-based sentiment scoring

Combined into a delta score:
- Positive delta → "inward fade" (relationship strengthening)
- Negative delta → "outward fade" (relationship cooling)

## Search

Built-in BM25 with Okapi parameters (k1=1.5, b=0.75). No external dependencies.

The `SearchBackend` protocol allows plugging in any search engine:

```python
class SearchBackend(Protocol):
    def index(self, doc_id: str, text: str) -> None: ...
    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]: ...
```

## File Layout

```
store/
├── staging/
│   └── YYYY-MM-DD.jsonl     # append-only, one JSON per line
└── archive/
    └── YYYY-MM-DD.json      # hash-chained documents
```

Everything is JSON. No binary formats. Portable — copy the directory to move the memory.
