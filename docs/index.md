# ASHA Documentation

**v0.4.2** - mission-aware agent governance (ANCHOR) plus drop-in security and optimization for LLM applications.

ASHA masks PII, reduces tokens, and checks for injection patterns before prompts reach a model. **ANCHOR** wraps autonomous agents with mission contracts, action guards, and OS sandboxing. The root API is `process`, `sanitize`, `optimize`, `Agent`, and `anchor`; everything else lives in subpackages.

> Developer preview - pin `asha==0.4.2` in production. APIs may change before 1.0.0.

---

## Start here

| Guide | Description |
|-------|-------------|
| [Getting Started](getting-started.md) | Install and first example |
| [Quickstart](quickstart.md) | 5-minute walkthrough |
| [ANCHOR Runtime](anchor.md) | Mission governance for agents |
| [API Reference](api-reference.md) | `process`, `sanitize`, `optimize`, `Agent`, `anchor` |
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

For autonomous agents, use `anchor(agent)` for mission-aware governance.

---

## Public imports

```python
# Root
from asha import process, sanitize, optimize, Agent, anchor

# Common advanced imports
from asha.integrations import wrap_llm
from asha.runtime.anchor import anchor_any
from asha.types import ProcessResult
from asha.core.policy_config import PolicyConfig
from asha.runtime import PromptProcessor
```

`wrap_llm`, `Pipeline`, `Processor`, and lazy root exports were **removed in v0.4.1**. See [deprecations.md](deprecations.md).

---

## Documentation map

### Essentials

- [ANCHOR](anchor.md) - agent governance, sandbox, adapters
- [Security](security.md) - PII masking, injection checks, modes
- [Optimization](optimization.md) - token reduction
- [Integrations](integrations.md) - FastAPI, LangChain, Instructor, etc.
- [Debugging](debugging.md) - `trace=True`, diffs

### Architecture

- [Architecture](architecture.md) - package layout and layer rules
- [Pipeline](pipeline.md) - processing flow (3 engines, not 7 stages)
- [Prompt IR](prompt-ir.md) - internal representation (not public API)
- [Routing](routing.md) - `Agent(routing_config=...)`

### Operations

- [Benchmarks](benchmarks.md) - performance numbers
- [Performance Tuning](performance-tuning.md) - speed vs security
- [Troubleshooting](troubleshooting.md) - common issues
- [FAQ](faq.md)

### Project

- [Developer Preview](developer-preview.md) - scope and limitations
- [Versioning](versioning.md) - release policy
- [Migration v0.4](migration-v0.4.md) - upgrade from 0.3.x
- [Deprecations](deprecations.md) - removed APIs
- [Roadmap](roadmap.md)
- [Contributing](contributing.md)

---

## Install

```bash
pip install asha   # Python 3.10+
pip install -e ".[docs]" && mkdocs serve   # local docs
```
