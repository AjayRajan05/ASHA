# Contributing to PrivySHA

Thank you for your interest in contributing!

## Quick Links

- **Full contributing guide**: [docs/contributing.md](docs/contributing.md)
- **Security reports**: [SECURITY.md](SECURITY.md) — do not open public issues for vulnerabilities
- **Code of conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Getting Started

```bash
git clone https://github.com/AjayRajan05/privySHA.git
cd privySHA
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Requirements

- Python **3.10+**
- Follow existing code style (Black, flake8)
- Add tests for new behavior in `tests_v2/`
- Keep changes focused — one concern per PR

## Pull Request Checklist

- [ ] Tests pass locally (`pytest`)
- [ ] New features include unit tests
- [ ] Documentation updated if API changes
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] No secrets or API keys committed

## Development Focus Areas

We especially welcome contributions in:

- PII detection accuracy and false-positive reduction
- Security bypass test cases
- Provider adapter compatibility
- Documentation and examples
- Benchmark reproducibility

See [docs/contributing.md](docs/contributing.md) for architecture overview, release process, and detailed guidelines.
