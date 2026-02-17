## What does this PR do?

<!-- Brief description of the change -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactor (no functional change)

## Checklist

- [ ] Tests pass (`python -m pytest tests/ -v`)
- [ ] No new dependencies added (zero-dependency constraint)
- [ ] Python 3.10+ compatible
- [ ] Docstrings updated for public API changes
- [ ] `README.md` updated if needed

## How was this tested?

<!-- Describe tests run, include cycle counts if relevant -->

## Related issues

<!-- Link any issues: Fixes #123, Relates to #456 -->

---

**COMB architecture context:**
- `active/` — current session documents
- `staging/` — daily rollup buffer  
- `archive/` — hash-chained immutable chain
- `links/` — honeycomb graph (temporal, semantic, social)

If your change touches the archive chain or link structure, please explain the integrity implications.
