# Contributing to PrivySHA

**v0.3.0 developer preview** — see [developer-preview.md](developer-preview.md) for release expectations.

Thank you for contributing! Small, focused PRs are welcome. Discuss large architectural changes in an issue first.

---

## Development setup

```bash
git clone https://github.com/AjayRajan05/privySHA.git
cd privySHA
pip install -e ".[dev]"
```

Optional extras for testing integrations:

```bash
pip install -e ".[dev,ml,integrations,local-advisor]"
```

Verify installation:

```bash
privysha quick-test
python examples/developer_preview_demo.py
```

---

## Project structure

```
src/privysha/
├── __init__.py          # Public API (eager + lazy exports)
├── agent.py             # Agent class
├── adapters/            # LLM provider adapters
├── cli/                 # CLI (main.py, benchmark_cli.py, recommend_cli.py)
├── compiler/            # Optimizer, MSDPC, prompt compiler
├── core/                # PolicyConfig, hybrid PII, trace, benchmark
├── integrations/        # FastAPI, LangChain, Instructor, etc.
├── ir/                  # Prompt IR
├── local_advisor/       # PrivyFit
├── pipeline/            # 7-stage pipeline
├── routing/             # ModelRouter
├── security/            # PII detection, patterns, masking
└── utils/               # dropin.py (process, wrap_llm, etc.)

tests/                   # Core tests
tests_v2/                # Extended tests
benchmarks/              # Benchmark harness
docs/                    # Documentation (MkDocs)
examples/                # Example scripts
```

---

## Running tests

```bash
# Default (skips integration tests requiring API keys)
pytest

# Include integration tests
pytest -m integration

# With coverage
pytest --cov=src --cov-fail-under=40

# Specific file
pytest tests/test_adapter_factory.py -v
```

Integration tests require API keys (`GEMINI_API_KEY`, etc.) and are skipped by default in CI.

---

## Code quality

```bash
# Format
black src/ tests/ tests_v2/

# Lint
flake8 src/ tests/ tests_v2/

# Type check
mypy src/privysha/
```

CI runs all of these on every push.

---

## Documentation

Docs are in `docs/` and built with MkDocs:

```bash
pip install -e ".[docs]"
mkdocs serve
```

When changing the public API, update:

- `docs/api-reference.md`
- `docs/core-concepts.md`
- Relevant feature docs

Navigation is defined in `mkdocs.yml`.

---

## Benchmarks

Before submitting performance-related changes:

```bash
python benchmarks/run_benchmarks.py --save
python benchmarks/run_benchmarks.py --compare benchmarks/baseline/results.json
```

Do not regress fail-safe rate (must remain 100%) or false positive rate (must remain 0%).

---

## Pull request guidelines

1. Fork and create a feature branch
2. Write tests for new behavior
3. Run `pytest` and `black` / `flake8`
4. Update docs if API changes
5. Keep PRs focused — one feature or fix per PR

---

## Release process

Current track: **0.3.x developer preview**.

Releases are triggered via GitHub Release or manual workflow dispatch. See [publishing.md](publishing.md).

Version is defined in:

- `pyproject.toml`
- `src/privysha/__init__.py` → `__version__`

Update `CHANGELOG.md` for every release.

---

## Public API policy

The stable surface for 0.3.x:

```python
from privysha import (
    process, wrap_llm, optimize, sanitize,
    process_async, optimize_async, sanitize_async,
    unmask, Agent, Pipeline, AdapterFactory,
    recommend_local_model, get_last_recommendation,
)
```

Advanced symbols are lazy-loaded. Changes to eager exports require discussion in an issue.

---

## Getting help

- [GitHub Issues](https://github.com/AjayRajan05/privySHA/issues) — bugs and features
- [GitHub Discussions](https://github.com/AjayRajan05/privySHA/discussions) — design questions

---

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
