# Contributing to COMB

Thank you for your interest in contributing to COMB!

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/amuzetnoM/comb/issues)
- Include: Python version, OS, minimal reproduction steps
- Check existing issues before opening a new one

### Pull Requests

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for any new functionality
4. Ensure all tests pass: `python -m pytest tests/`
5. Follow the existing code style (see below)
6. Submit a PR with a clear description

### Code Style

- Type hints on all public functions and methods
- Docstrings on all public classes and methods (Google style)
- No external dependencies in core (`comb/` package) — stdlib only
- `ruff` for linting (if available)
- Keep it simple. Ship it.

### Testing

```bash
python -m pytest tests/ -v
```

All tests must pass with zero dependencies (no pytest plugins required, but pytest itself is needed to run them).

### What We're Looking For

- Bug fixes
- Documentation improvements
- Search backend implementations
- Performance improvements
- Test coverage improvements

### What We're NOT Looking For

- Adding required dependencies to core
- Changing the storage format without discussion
- Features that break single-directory portability

## Development Setup

```bash
git clone https://github.com/amuzetnoM/comb.git
cd comb
pip install -e ".[cli]"
python -m pytest tests/
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
