
# Contributing to ECG2Signal

We welcome contributions! Here's how to get started:

## Development Setup

```bash
git clone https://github.com/yourusername/ecg2signal.git
cd ecg2signal
pip install -e ".[dev]"
pre-commit install
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

## Testing

```bash
pytest tests/ -v --cov
```

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a PR

## Code Review

All PRs require:
- Passing tests
- Code review approval
- Documentation updates

## License

By contributing, you agree to license your contributions under Apache 2.0.
