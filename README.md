```
     _____ _____ _____ _____
    / ____/ ___ / _  \/ _  \     COMB
   / /   / / / / / / / /_/ /     Chain-Ordered Memory Base
  / /___/ /_/ / / / / ___ /
  \____/\___/_/ /_/_/   \_\      Lossless context archival
                                  for AI agents.
```

# COMB

**Your AI doesn't need a better summary. It needs a better memory.**

COMB is a honeycomb-structured, lossless context archival system for AI agents. Instead of summarizing conversations (lossy), COMB archives the full text as documents in a three-directional graph.

Zero dependencies. Pure Python. Single directory storage. Copy the folder, copy the memory.

---

## Why not just summarize?

Every AI memory system today works the same way: conversations get summarized, compressed, or embedded into vectors. Information is lost at every step. Important details — the user's exact phrasing, the nuance of a disagreement, the specific numbers discussed — vanish.

COMB takes a different approach: **keep everything**.

- **Lossless** — full conversation text, always recoverable
- **Hash-chained** — tamper-evident, like a blockchain for conversations
- **Three-directional links** — navigate by time, by meaning, or by relationship
- **Schema-on-read** — your data, your interpretation
- **Serverless** — no database, no server, just files in a directory

## Architecture

```
                    ┌─────────┐
               ╱╲   │ Tier 1  │   Agent's context window
              ╱  ╲  │ Active  │   (not managed by COMB)
             ╱    ╲ └─────────┘
            ╱      ╲
    ┌──────╱────────╲──────┐
    │      Tier 2          │   Today's conversation dumps
    │   Daily Staging      │   Append-only JSONL
    │   (append-only)      │
    └──────────┬───────────┘
               │ rollup()
    ┌──────────▼───────────┐
    │      Tier 3          │   One document per day
    │   Chain Archive      │   Hash-chained
    │                      │   Honeycomb-linked
    └──────────────────────┘

         The Honeycomb:

         TEMPORAL ←──→  chronological chain (prev/next)
         SEMANTIC ←──→  content similarity links
         SOCIAL   ←──→  relationship gradient links
```

## Quick Start

```bash
pip install comb-db
```

```python
from comb import CombStore

# Create a store (just a directory)
store = CombStore("./my-memory")

# Stage today's conversations
store.stage("User asked about encryption. Assistant explained AES-256...")
store.stage("User clarified they need RSA for key exchange...")

# Roll up into the archive
doc = store.rollup()
# → hash-chained, semantic + social links computed automatically

# Search
results = store.search("encryption")
for r in results:
    print(r.date, r.similarity_score)

# Navigate the honeycomb
doc = store.get("2026-02-17")
doc.temporal.prev          # previous day
doc.semantic.neighbors     # similar conversations
doc.social.strengthened    # deepening relationships
doc.social.cooled          # cooling relationships

# Verify integrity
assert store.verify_chain()  # no tampering
```

## CLI

```bash
# Stage from stdin
echo "Today's conversation..." | comb -s ./my-memory stage

# Stage from file
comb -s ./my-memory stage -f conversation.txt

# Roll up
comb -s ./my-memory rollup

# Search
comb -s ./my-memory search "encryption"

# Show a document
comb -s ./my-memory show 2026-02-17

# Verify chain
comb -s ./my-memory verify

# Stats
comb -s ./my-memory stats
```

Requires `pip install comb-db[cli]`.

## The Honeycomb

Every archived document has three types of links:

### Temporal Links
A chronological chain. Each document points to the previous and next day. Hash-linked — if any document is tampered with, the chain breaks.

### Semantic Links
Computed via term-frequency cosine similarity (built-in, no dependencies). The top-k most similar documents are linked automatically during rollup. Plug in your own search backend for better results.

### Social Links
The novel part. Conversations have *relational temperature*. COMB tracks:

- **Inward fade** (strengthening) — engagement is increasing, sentiment is warming
- **Outward fade** (cooling) — engagement is decreasing, sentiment is cooling

This lets an agent understand not just *what* was discussed, but *how the relationship evolved*.

## Custom Search Backend

The built-in BM25 is good enough for hundreds of documents. For scale, implement the `SearchBackend` protocol:

```python
from comb import SearchBackend

class MyBackend:
    def index(self, doc_id: str, text: str) -> None:
        ...
    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        ...

store = CombStore("./memory", search_backend=MyBackend())
```

## What COMB Is

- A file-based archival system for conversation history
- A tamper-evident chain of daily conversation documents
- A three-directional graph for navigating memory
- A library with zero required dependencies
- Portable (copy the directory, copy the memory)

## What COMB Is Not

- Not a vector database
- Not a summarization tool
- Not a real-time retrieval system
- Not a replacement for your agent's context window
- Not magic — it's just well-organized files

## Storage Format

Everything is JSON. Human-readable. No binary formats. No proprietary encodings.

```
my-memory/
├── staging/
│   └── 2026-02-17.jsonl    # today's staged conversations
└── archive/
    ├── 2026-02-15.json     # archived, hash-chained
    ├── 2026-02-16.json     # with honeycomb links
    └── 2026-02-17.json
```

## Requirements

- Python 3.10+
- Zero dependencies (stdlib only)
- Optional: `click` for CLI

## Lineage

COMB descends from HYBRIDbee, a serverless document database. It inherits the philosophy: schema-on-read, single-directory storage, zero configuration.

## License

MIT

## Author

Ava Shakil — [Artifact Virtual](https://artifactvirtual.com)
