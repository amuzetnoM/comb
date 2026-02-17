# Contributing to COMB

Thanks for considering contributing to COMB! Here's how to get started.

## Setup

```bash
git clone https://github.com/amuzetnoM/comb.git
cd comb
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Principles

1. **Zero dependencies.** COMB uses only Python stdlib. If your change needs an external package, it won't be merged. Period.
2. **Python 3.10+.** No f-string walrus operators or other 3.12+ features.
3. **Lossless.** Never discard data. Archive integrity is non-negotiable.
4. **Tests.** Every new feature needs tests. Every bug fix needs a regression test.

## Architecture

COMB has three tiers:
- **Active** — current session, mutable
- **Staging** — daily buffer, append-only
- **Archive** — hash-chained, immutable, forever

And three link directions:
- **Temporal** — chronological chain (hash-linked)
- **Semantic** — content similarity (BM25)
- **Social** — relationship gradient tracking

## What we're looking for

- Performance improvements (especially search)
- Better semantic linking algorithms
- Social gradient tracking enhancements
- Documentation and examples
- Language bindings (Rust, TypeScript, Go)
- Integration examples with AI frameworks

## What we're NOT looking for

- Adding dependencies
- Summarization or lossy compression
- Breaking the archive chain format
- Changes that drop Python 3.10 support

## Process

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-thing`)
3. Write tests first
4. Make your changes
5. Run `python -m pytest tests/ -v` (all 35+ must pass)
6. Push and open a PR using the template

## Code style

- Type hints on public APIs
- Docstrings on public classes and functions
- Keep it simple. Readable > clever.

## License

By contributing, you agree your code is released under the MIT License.
