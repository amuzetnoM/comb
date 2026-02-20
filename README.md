<p align="center">
  <pre align="center">
     _____ _____ _____ _____
    / ____/ ___ / _  \/ _  \     COMB
   / /   / / / / / / / /_/ /     Chain-Ordered Memory Base
  / /___/ /_/ / / / / ___ /
  \____/\___/_/ /_/_/   \_\      Lossless context archival
                                  for AI agents.
  </pre>
</p>

<p align="center">
  <em>A 200K context window has everything but finds nothing.<br/>COMB has everything and finds what matters.</em>
</p>

<p align="center">
  <strong>Three lines to remember everything. Zero dependencies.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#the-honeycomb">The Honeycomb</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#cli">CLI</a> •
  <a href="#custom-search-backend">Custom Search</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/comb-db/"><img src="https://img.shields.io/pypi/v/comb-db?color=blue&logo=pypi&logoColor=white" alt="PyPI"/></a>
  <a href="https://pypi.org/project/comb-db/"><img src="https://img.shields.io/pypi/pyversions/comb-db?logo=python&logoColor=white" alt="Python versions"/></a>
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Zero deps"/>
  <img src="https://img.shields.io/badge/storage-JSON-orange" alt="JSON"/>
  <img src="https://img.shields.io/badge/chain-hash--linked-blueviolet" alt="Hash-linked"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT"/>
</p>

---

COMB is a honeycomb-structured, lossless context archival system for AI agents. Instead of summarizing conversations (lossy), COMB archives the full text as documents in a three-directional graph.

Zero dependencies. Pure Python. Single directory storage. Copy the folder, copy the memory.

## Why not just summarize?

Every AI memory system today works the same way: conversations get summarized, compressed, or embedded into vectors. Information is lost at every step. Important details — the user's exact phrasing, the nuance of a disagreement, the specific numbers discussed — vanish.

COMB takes a different approach: **keep everything**.

| | Principle | |
|---|---|---|
| 🔒 | **Lossless** | Full conversation text, always recoverable |
| ⛓️ | **Hash-chained** | Tamper-evident, like a blockchain for conversations |
| 🐝 | **Three-directional links** | Navigate by time, by meaning, or by relationship |
| 📐 | **Schema-on-read** | Your data, your interpretation |
| 📁 | **Serverless** | No database, no server, just files in a directory |

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
```

```
comb/
├── core.py          # CombStore — the main interface
├── staging.py       # DailyStaging — append-only JSONL staging
├── archive.py       # ChainArchive — hash-chained document store
├── document.py      # CombDocument — temporal, semantic, social links
├── honeycomb.py     # HoneycombGraph — three-directional link computation
├── search.py        # BM25Search — zero-dependency full-text search
├── cli.py           # Click CLI — stage, rollup, search, show, verify, stats
└── _utils.py        # Hashing, date helpers
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

## The Honeycomb

Every archived document lives in a three-directional graph:

```
         TEMPORAL ←──→  chronological chain (prev/next hash-linked)
         SEMANTIC ←──→  content similarity (BM25 cosine, top-k neighbors)
         SOCIAL   ←──→  relationship gradient (warming ↔ cooling)
```

### ⛓️ Temporal Links
A chronological chain. Each document points to the previous and next day. Hash-linked — if any document is tampered with, the chain breaks. Blockchain-grade integrity for conversation history.

### 🧠 Semantic Links
Computed via term-frequency cosine similarity (built-in, zero dependencies). The top-k most similar documents are linked automatically during rollup. Plug in your own search backend for better results.

### 💛 Social Links
The novel part. Conversations have *relational temperature*. COMB tracks:

- **Inward fade** (strengthening) — engagement is increasing, sentiment is warming
- **Outward fade** (cooling) — engagement is decreasing, sentiment is cooling

This lets an agent understand not just *what* was discussed, but *how the relationship evolved*.

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

# Blink (pre-restart flush)
echo "operational context..." | comb -s ./my-memory blink

# Recall (post-restart wake-up)
comb -s ./my-memory recall

# Show a document
comb -s ./my-memory show 2026-02-17

# Verify chain integrity
comb -s ./my-memory verify

# Stats
comb -s ./my-memory stats
```

Requires `pip install comb-db[cli]`.

## The Blink Pattern

Seamless agent restarts with zero context loss. Flush before the wall, recall after the restart.

```python
# Before restart — save everything
store.blink("""
Active project: step 3500/100K, loss 4.85
Decision: deferred publish until 80% milestone
""")

# After restart — get it all back
context = store.recall()
# → staged entries (most recent) + archived history
```

The agent doesn't die and resurrect. It **blinks**. See [docs/blink.md](docs/blink.md) for the full pattern.

## Custom Search Backend

The built-in BM25 is good enough for hundreds of documents. For scale, implement the `SearchBackend` protocol:

```python
from comb import SearchBackend

class MyVectorBackend:
    def index(self, doc_id: str, text: str) -> None:
        ...
    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        ...

store = CombStore("./memory", search_backend=MyVectorBackend())
```

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

## What COMB Is — and Isn't

**Is:**
- A file-based archival system for conversation history
- A tamper-evident chain of daily conversation documents
- A three-directional graph for navigating memory
- A zero-dependency library. Portable. Copy the directory, copy the memory.

**Isn't:**
- Not a vector database
- Not a summarization tool
- Not a real-time retrieval system
- Not a replacement for your agent's context window

## Lineage

COMB descends from HYBRIDbee, a serverless document database. It inherits the philosophy: schema-on-read, single-directory storage, zero configuration.

## Requirements

- Python 3.10+
- Zero dependencies (stdlib only)
- Optional: `click` for CLI

## License

MIT

---

<p align="center">
  <em>Built by <a href="https://github.com/amuzetnoM">Ava Shakil</a> at <a href="https://github.com/Artifact-Virtual">Artifact Virtual</a></em>
</p>
