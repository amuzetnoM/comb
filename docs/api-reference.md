# API Reference

## CombStore

The main entry point.

### `CombStore(path, *, search_backend=None)`

Create or open a COMB store.

- `path` — directory for all data (created if needed)
- `search_backend` — optional `SearchBackend` implementation (default: BM25)

### `store.stage(text, *, metadata=None, date=None)`

Append text to today's staging (Tier 2).

### `store.rollup(date=None) -> CombDocument | None`

Roll up staged data into the archive (Tier 2 → Tier 3). Returns the archived document, or `None` if nothing was staged.

### `store.search(query, *, mode="bm25", k=5) -> list[CombDocument]`

Search the archive. Each result has `similarity_score` set.

### `store.get(date) -> CombDocument | None`

Retrieve a document by date string (YYYY-MM-DD).

### `store.walk(start, *, direction="temporal", depth=100) -> Iterator[CombDocument]`

Walk the honeycomb graph. Directions: `"temporal"` (forward chain), `"semantic"` (breadth-first by similarity).

### `store.verify_chain() -> bool`

Verify hash chain integrity.

### `store.stats() -> dict`

Returns: `document_count`, `total_bytes`, `chain_length`, `semantic_links`, `social_links`, `staged_dates`, `chain_valid`.

---

## CombDocument

A single archived document.

### Attributes

- `date: str` — YYYY-MM-DD
- `content: str` — full archived text
- `hash: str` — SHA-256 chain hash
- `prev_hash: str | None` — previous document's hash
- `metadata: dict` — arbitrary metadata
- `temporal: TemporalLinks` — `.prev`, `.next` (date strings or None)
- `semantic: SemanticLinks` — `.neighbors` (list of `SemanticNeighbor`)
- `social: SocialLinks` — `.links`, `.strengthened`, `.cooled`
- `similarity_score: float | None` — set during search (transient)

### Methods

- `to_dict() -> dict` — serialize
- `from_dict(d) -> CombDocument` — deserialize
- `to_json(**kwargs) -> str` — JSON string
- `from_json(raw) -> CombDocument` — from JSON string

---

## SearchBackend (Protocol)

```python
class SearchBackend(Protocol):
    def index(self, doc_id: str, text: str) -> None: ...
    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]: ...
```

## BM25Search

Built-in BM25 implementation. Implements `SearchBackend`.

- `BM25Search(k1=1.5, b=0.75)`
- `index(doc_id, text)` — index a document
- `search(query, k=5)` — search, returns `(doc_id, score)` tuples
- `remove(doc_id)` — remove from index
