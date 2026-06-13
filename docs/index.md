# PrivySHA Documentation

**Drop-in security + optimization layer for LLM apps** (v0.3.0 developer preview)

PrivySHA masks PII, reduces tokens, and blocks prompt injection — with minimal code changes. See [Developer Preview](developer-preview.md) for scope and limitations.

---

## Quick start

| Guide | Description |
|-------|-------------|
| [Getting Started](getting-started.md) | Install and first example |
| [Quickstart](quickstart.md) | 5-minute walkthrough |
| [API Reference](api-reference.md) | `process`, `wrap_llm`, `optimize`, `sanitize`, `Agent` |
| [Examples](examples.md) | Real-world patterns |
| [Local Model Advisor](local-advisor.md) | PrivyFit — recommend local LLMs |

---

## Core documentation

### Essential

- [Core Concepts](core-concepts.md) — modes, PII detection, pipeline overview
- [Security](security.md) — PII masking, injection protection, fail-open vs fail-closed
- [Optimization](optimization.md) — token reduction and cost savings
- [Integrations](integrations.md) — FastAPI, LangChain, Instructor, Guardrails

### Advanced

- [Architecture](architecture.md) — package layout and design
- [Pipeline](pipeline.md) — 7-stage processing flow
- [Prompt IR](prompt-ir.md) — intermediate representation
- [Routing](routing.md) — model selection strategies
- [Debugging](debugging.md) — `TraceContext` and pipeline traces

### Operations

- [Benchmarks](benchmarks.md) — reproducible performance numbers
- [Performance Tuning](performance-tuning.md) — speed vs security trade-offs
- [Troubleshooting](troubleshooting.md) — common issues
- [FAQ](faq.md) — frequently asked questions

### Project

- [Versioning](versioning.md) — release policy and timeline
- [Migration](migration.md) — upgrade from Presidio, regex, spaCy, etc.
- [Compliance](compliance.md) — GDPR, CCPA considerations (tool-only)
- [Contributing](contributing.md) — development guide
- [Publishing](publishing.md) — PyPI trusted publishing
- [Roadmap](roadmap.md) — planned features

---

## Why PrivySHA?

### Without PrivySHA

```
User Prompt → LLM → Response
```

Problems: unstructured prompts, PII leakage, high token cost, no debugging visibility.

### With PrivySHA

```
User Prompt → Security → IR → Optimization → LLM → Response
```

Benefits: PII masking, 5–15% typical token reduction (see [benchmarks](benchmarks.md)), pipeline traces, optional local model routing via PrivyFit.

---

## Installation

```bash
pip install privysha
```

Requires Python 3.10+. From source:

```bash
pip install -e .
python examples/developer_preview_demo.py
```

Build docs locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

---

## Primary API

```python
from privysha import process

# Returns optimized string by default
result = process("My email is alex@company.com — analyze this dataset.")
print(result)

# With metrics
result = process("...", return_metrics=True)
print(result["optimized"])
print(result["token_reduction"])
```

See [API Reference](api-reference.md) for `wrap_llm`, `optimize`, `sanitize`, `Agent`, and `recommend_local_model`.

---

## Community

- **GitHub**: [AjayRajan05/privySHA](https://github.com/AjayRajan05/privySHA)
- **Issues**: [Report bugs](https://github.com/AjayRajan05/privySHA/issues)
- **License**: Apache 2.0
