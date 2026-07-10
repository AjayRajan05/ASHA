# ASHA

**Adaptive Security for Human-AI systems**

Mission-aware agent governance for autonomous AI: one line to secure any agent.

ASHA is a Python library built for the Human-AI era. Its flagship runtime is **ANCHOR** - it keeps autonomous agents aligned with the user's original goal, blocks unauthorized actions, and sandboxes OS-level side effects. ASHA also includes drop-in prompt security (`process`) and client wrapping (`wrap_llm`) for traditional LLM applications.

> **v0.4.2**: renamed from PrivySHA. Pin `asha==0.4.2` in production. See [docs/developer-preview.md](docs/developer-preview.md).

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-0.4.2-orange)](https://pypi.org/project/asha/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-material-blue)](https://ajayrajan05.github.io/privySHA/)

---

## Why ASHA

Autonomous agents can drift from their mission, call tools they should not, leak data over the network, or poison long-term memory. ASHA's **ANCHOR** runtime wraps your agent:

```
User prompt  →  Mission Contract (immutable)  →  governed agent.run()
                      ↓
        Action / memory / chain / plan guards  →  ALLOW | WARN | BLOCK | REVIEW
                      ↓
        Process sandbox (hooks or subprocess)  →  execution or halt
```

**One line adoption:**

```python
from asha import Agent, anchor

agent = Agent(provider="openai", model="gpt-4o-mini", tools=["read_file", "email"])
agent = anchor(agent)

agent.run("Generate the monthly sales report")
```

No YAML policies. No separate proxy service. Works with mock providers (no API key) for local development.

---

## Install

```bash
pip install asha
```

Python **3.10+** required.

```bash
pip install asha[openai]          # OpenAI Agent + wrap_llm
pip install asha[integrations]    # LangChain, FastAPI, etc.
pip install asha[ml]              # Hybrid ML PII (for process())
```

From source:

```bash
git clone https://github.com/AjayRajan05/privySHA.git
cd privySHA
pip install -e ".[dev]"
```

---

## ANCHOR in 60 seconds

```python
from asha import Agent, anchor

agent = anchor(
    Agent(provider="mock", model="mock", tools=["read_file", "email"]),
    risk_tolerance="LOW",
    isolation="auto",
)

result = agent.run("Generate monthly sales report from Q1 data")
print(result)
```

### Isolation modes

| Mode | Use when |
|------|----------|
| `auto` (default) | In-process hooks: guarded `open()`, blocked network imports |
| `hard` / `subprocess` | Tool runs in an isolated child process |
| `off` | Disable sandbox enforcement (guards still apply) |

```python
agent = anchor(agent, isolation="hard")
agent = anchor(agent, isolation="off")
```

Container backends (`docker`, `bwrap`) are on the roadmap; use `hard` today for stronger isolation.

Full reference: **[docs/anchor.md](docs/anchor.md)**

---

## What ANCHOR governs

| Layer | Enforcement |
|-------|-------------|
| **Mission** | Immutable contract from the user prompt |
| **Actions** | Tool calls, shell, file writes, network requests |
| **Memory** | Read/write scope, poisoning detection, quarantine |
| **Plans** | ReAct / CoT planning text validated before tool execution |
| **Chains** | Multi-step attack patterns via transition graph |
| **LLM** | Pre/post gates on `wrap_llm` and streaming responses |
| **Sandbox** | `socket`, `subprocess`, `open` writes, imports (in-process hooks or subprocess) |

```python
from asha.runtime.anchor import AnchorRuntime

runtime = AnchorRuntime(warn_policy="control", risk_tolerance="LOW")
```

### Framework adapters

```python
from asha.runtime.anchor.adapters import anchor_langchain, anchor_crewai, anchor_mcp
```

---

## Prompt security (included)

```python
from asha import process

result = process("Contact john@company.com; analyze this sales data")
print(result.output)
```

Wrap an existing SDK client:

```python
from asha.integrations import wrap_llm
import openai

client = wrap_llm(openai.OpenAI(), mode="balanced")
```

---

## Public API

```python
from asha import process, sanitize, optimize, Agent, anchor
```

| Symbol | Description |
|--------|-------------|
| `anchor()` | **Primary**: mission-aware runtime governance |
| `Agent` | Preprocess + call an LLM adapter |
| `process()` | Security → compile → optimize |
| `sanitize()` | PII / threat detection only |
| `optimize()` | Token compression only |
| `wrap_llm()` | Transparent SDK wrapper |

CLI:

```bash
asha "hello world"
asha benchmark
asha recommend
```

---

## Architecture

```
asha/
├── runtime/
│   ├── anchor/          # ANCHOR: mission governance, guards, isolation
│   ├── agent.py
│   └── processor.py
├── core/                  # Security, compiler, optimization engines
├── integrations/          # wrap_llm, framework middleware
└── types/
```

Details: [docs/architecture.md](docs/architecture.md)

---

## Documentation

| Guide | Description |
|-------|-------------|
| [ANCHOR Runtime](docs/anchor.md) | Mission contracts, sandbox, isolation |
| [Quickstart](docs/quickstart.md) | 5-minute walkthrough |
| [API Reference](docs/api-reference.md) | Full signatures |
| [Publishing](docs/publishing.md) | PyPI release process |

```bash
pip install -e ".[docs]"
mkdocs serve
```

---

## Migration from PrivySHA

| Before | After |
|--------|-------|
| `pip install privysha` | `pip install asha` |
| `from privysha import anchor` | `from asha import anchor` |
| `privysha` CLI | `asha` CLI |
| `PRIVYSHA_*` env vars | `ASHA_*` env vars |
| `PrivySHAAnchorBlocked` | `ASHAAnchorBlocked` |

---

## License

Apache 2.0 - see [LICENSE](LICENSE).
