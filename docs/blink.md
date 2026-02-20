# The Blink Pattern

Seamless agent restarts with zero context loss.

## The Problem

AI agents hit context limits. When they do, conversations get compacted into summaries — lossy, fuzzy, missing the details that matter. The agent wakes up foggy.

## The Solution

**Blink**: flush everything to COMB *before* the restart, then recall it *after*.

```
flush → stage COMB → restart → recall → resume
```

The agent doesn't die and resurrect. It blinks.

## How It Works

### Before Restart (the flush)

```python
from comb import CombStore

store = CombStore("./agent-memory")

# Stage everything the agent needs to remember
store.blink("""
## Active Projects
- Training run: step 3500/100K, loss 4.85
- PR #42: waiting on review

## Key Decisions
- Using 16K tokenizer (2x compression over 8K)
- Deferred arXiv until 80% milestone

## What Just Happened
- Fixed checkpoint loading crash
- Created new cron job for monitoring
""")
```

### After Restart (the recall)

```python
store = CombStore("./agent-memory")

# Get everything back
context = store.recall()
# → Returns staged entries + recent archive, most recent first
```

### CLI

```bash
# Before restart
echo "operational context..." | comb -s ./memory blink

# After restart
comb -s ./memory recall

# Blink + roll up into permanent archive
echo "context..." | comb -s ./memory blink --rollup
```

## With Auto-Restart

For OpenClaw agents or similar frameworks, wire blink into your restart hook:

```bash
#!/bin/bash
# auto-flush.sh — flush + restart

# 1. Stage to COMB
comb -s ./memory blink "$FLUSH_TEXT"

# 2. Restart the agent process
restart-agent

# 3. On wake, the agent's init script runs:
#    context = store.recall()
```

## API Reference

### `CombStore.blink(text, *, metadata=None, rollup=False)`

Stage operational context and prepare for restart.

- **text**: Everything the agent needs to remember.
- **metadata**: Optional dict attached to the staged entry. A `"blink": True` flag is added automatically.
- **rollup**: If `True`, also promotes staged data to the permanent archive.
- **Returns**: Preview of what `recall()` will return.

### `CombStore.recall(*, k=5, include_staged=True)`

Reconstruct operational context after restart.

- **k**: Number of recent archived documents to include.
- **include_staged**: Whether to include un-rolled staged entries (usually yes).
- **Returns**: Concatenated context text, staged entries first (most recent), then archived.

## Why This Works

1. **Staged entries survive restarts** — they're on disk, not in memory.
2. **Recall is selective** — recent context first, not the entire history.
3. **Search still works** — need something from 3 weeks ago? `store.search("deadlines")`.
4. **Chain integrity preserved** — every blink is timestamped and hash-linked.
5. **Zero dependencies** — pure Python, just files on disk.

## The Insight

> A 200K context window has everything but finds nothing.
> COMB has everything and finds what matters.

The blink doesn't lose information — it *organizes* it. The transition from one context window to the next becomes invisible. Not death and resurrection. Just... a blink. 🔮
