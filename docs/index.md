# PrivySHA Documentation

**v0.4.1** — drop-in security and optimization for LLM applications.

PrivySHA masks PII, reduces tokens, and checks for injection patterns before prompts reach a model. The root API is four functions plus `Agent`; everything else lives in subpackages.

> Developer preview — pin `privysha==0.4.1` in production. APIs may change before 1.0.0.

---

## Start here

| Guide | Description |
|-------|-------------|
| [Getting Started](getting-started.md) | Install and first example |
| [Quickstart](quickstart.md) | 5-minute walkthrough |
| [API Reference](api-reference.md) | `process`, `sanitize`, `optimize`, `Agent` |
| [Core Concepts](core-concepts.md) | Modes, results, policy |
| [Examples](examples.md) | Common patterns |

---

## How it works

```
Input prompt
    → Security (PII + threats)
    → Compile (internal IR → structured prompt)
    → Optimize (token compression)
    → ProcessResult
```

For LLM apps, add `wrap_llm(client)` or use `Agent` to preprocess before generation.

---

## Public imports

```python
# Root — only these four (+ __version__)
from privysha import process, sanitize, optimize, Agent

# Common advanced imports
from privysha.integrations import wrap_llm
from privysha.types import ProcessResult
from privysha.core.policy_config import PolicyConfig
from privysha.runtime import PromptProcessor
```

`wrap_llm`, `Pipeline`, `Processor`, and lazy root exports were **removed in v0.4.1**. See [deprecations.md](deprecations.md).

---

## Documentation map

### Essentials

- [Security](security.md) — PII masking, injection checks, modes
- [Optimization](optimization.md) — token reduction
- [Integrations](integrations.md) — FastAPI, LangChain, Instructor, etc.
- [Debugging](debugging.md) — `trace=True`, diffs

### Architecture

- [Architecture](architecture.md) — package layout and layer rules
- [Pipeline](pipeline.md) — processing flow (3 engines, not 7 stages)
- [Prompt IR](prompt-ir.md) — internal representation (not public API)
- [Routing](routing.md) — `Agent(routing_config=...)`

### Operations

- [Benchmarks](benchmarks.md) — performance numbers
- [Performance Tuning](performance-tuning.md) — speed vs security
- [Troubleshooting](troubleshooting.md) — common issues
- [FAQ](faq.md)

### Project

- [Developer Preview](developer-preview.md) — scope and limitations
- [Versioning](versioning.md) — release policy
- [Migration v0.4](migration-v0.4.md) — upgrade from 0.3.x
- [Deprecations](deprecations.md) — removed APIs
- [Roadmap](roadmap.md)
- [Contributing](contributing.md)

---

## Install

```bash
pip install privysha   # Python 3.10+
pip install -e ".[docs]" && mkdocs serve   # local docs
```
