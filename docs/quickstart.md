# Quick Start

Get COMB running in 30 seconds.

## Install

```bash
pip install comb-db
```

## Use

```python
from comb import CombStore

# 1. Create a store
store = CombStore("./my-memory")

# 2. Stage conversations throughout the day
store.stage("User asked about project deadlines. Assistant provided timeline...")
store.stage("Follow-up: user wants weekly check-ins instead of daily.")

# 3. Roll up into the archive
doc = store.rollup()
print(f"Archived: {doc.date}, hash: {doc.hash[:16]}...")

# 4. Search later
for result in store.search("deadlines"):
    print(f"  {result.date}: score {result.similarity_score:.3f}")

# 5. Navigate
doc = store.get("2026-02-17")
if doc:
    print(f"Previous: {doc.temporal.prev}")
    print(f"Similar: {[n.target for n in doc.semantic.neighbors]}")
    print(f"Warming: {[l.target for l in doc.social.strengthened]}")
```

## CLI

```bash
pip install comb-db[cli]

# Stage
echo "Today's conversation" | comb -s ./my-memory stage

# Roll up
comb -s ./my-memory rollup

# Search
comb -s ./my-memory search "deadlines"

# Verify chain integrity
comb -s ./my-memory verify
```

## Next Steps

- Read [Architecture](architecture.md) for how it works under the hood
- Read [API Reference](api-reference.md) for the full API
- Implement a custom `SearchBackend` for better semantic search
