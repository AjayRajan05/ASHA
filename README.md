# PrivySHA

**Drop-in security and token optimization for LLM apps** — mask PII, block injection patterns, and compress prompts before they reach any model.

> **v0.4.1 developer preview** — architecture-stable, API may evolve before 1.0.0. Pin your version in production. See [docs/developer-preview.md](docs/developer-preview.md).

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.4.1-orange)](https://pypi.org/project/privysha/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Status](https://img.shields.io/badge/status-developer%20preview-orange)](docs/developer-preview.md)

---

## What it does

```
Your app  →  process() / wrap_llm()  →  safe, smaller prompt  →  LLM
```

PrivySHA sits between your application and the model. One function call can:

- Mask emails, phones, API keys, and other PII
- Run prompt-injection checks
- Compress verbose prompts to save tokens
- Return typed results with metrics and optional traces

No global config. No pipeline boilerplate. Works without API keys for preprocessing.

---

## Install

```bash
pip install privysha
```

Python **3.10+** required. From source:

```bash
pip install -e .
```

Optional extras:

```bash
pip install privysha[openai]        # OpenAI client wrapping
pip install privysha[ml]              # Hybrid ML PII detection
pip install privysha[integrations]  # FastAPI, LangChain, etc.
```

---

## 60-second example

```python
from privysha import process

result = process("Contact john@company.com — analyze this sales data")
print(result)                    # str(result) → optimized output
print(result.output)             # same text, typed access
print(result.security.pii_detected)
print(result.metrics.token_reduction_pct)
```

**Wrap an existing client** (recommended for production):

```python
from privysha.integrations import wrap_llm
import openai

client = wrap_llm(openai.OpenAI(), mode="balanced")
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Email me at john@corp.com"}],
)
```

---

## Public API

Root package exports **five symbols only**:

```python
from privysha import process, sanitize, optimize, Agent
```

Everything else uses explicit subpackage imports:

```python
from privysha.integrations import wrap_llm, auto_patch
from privysha.runtime import PromptProcessor
from privysha.types import ProcessResult, SanitizeResult
from privysha.core.policy_config import PolicyConfig
```

| Function | What it does |
|----------|--------------|
| `process()` | Security → compile → optimize (full path) |
| `sanitize()` | Security / PII only |
| `optimize()` | Token compression only |
| `Agent` | Preprocess + call an LLM adapter |
| `wrap_llm()` | Transparent SDK wrapper (integrations) |

---

## Modes

```python
process(prompt, mode="balanced")  # default — fail-open with fallback
process(prompt, mode="strict")    # fail-closed — raises on total failure
process(prompt, mode="lite")      # minimal policy features
process(prompt, mode="off")       # passthrough, no changes
```

Advanced options go in `PolicyConfig`, not loose kwargs:

```python
from privysha.core.policy_config import PolicyConfig

process(
    prompt,
    policy=PolicyConfig(
        pii_mode="hybrid",      # needs privysha[ml]
        reversible=True,
        preserve_intent=True,
    ),
)
```

---

## Agent (preprocess + LLM)

```python
from privysha import Agent

agent = Agent(model="mock")  # no API key needed for mock
print(agent.run("Summarize data from john@example.com"))
```

With a real provider, set `OPENAI_API_KEY` and use `model="gpt-4o-mini"`.

---

## Architecture (v0.4.1)

```
privysha/
├── core/           # engines: security, compiler, policy
├── runtime/        # PromptProcessor, Agent, adapters
├── integrations/   # wrap_llm, auto_patch, framework middleware
├── types/          # ProcessResult, SanitizeResult
├── utils/          # drop-in functions
├── compat/         # opt-in legacy dict helpers
└── cli/            # privysha command
```

`process()` → `PromptProcessor` → three engines: **security**, **compile**, **optimize**.

Details: [docs/architecture.md](docs/architecture.md)

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Quickstart](docs/quickstart.md) | 5-minute walkthrough |
| [Getting Started](docs/getting-started.md) | Install, modes, CLI |
| [API Reference](docs/api-reference.md) | Full signatures |
| [Security](docs/security.md) | PII, masking, fail-closed |
| [Migration v0.4](docs/migration-v0.4.md) | Upgrading from 0.3.x |
| [Deprecations](docs/deprecations.md) | Removed symbols |

Build docs locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

---

## Tests

```bash
pip install -e ".[dev]"
pytest tests -q
```

CI runs on Ubuntu, Windows, and macOS (Python 3.10–3.12).

---

## Status

| Ready for | Not yet |
|-----------|---------|
| Pinned production pilots (`privysha==0.4.1`) | Stable 1.0 API guarantee |
| `process()` / `wrap_llm()` drop-in use | Certified compliance product |
| Architecture-frozen 0.4.x line | Unpinned dep without migration budget |

Stable public API is planned for **1.0.0** after a freeze period on 0.5.x. See [docs/versioning.md](docs/versioning.md).

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
