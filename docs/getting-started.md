# Getting Started with PrivySHA

**v0.3.0 developer preview** — see [developer-preview.md](developer-preview.md) for scope.

This guide installs PrivySHA and runs your first optimized, privacy-safe prompt.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from PyPI

```bash
pip install privysha
```

### Optional extras

```bash
pip install privysha[openai]       # OpenAI adapter
pip install privysha[anthropic]    # Anthropic adapter
pip install privysha[gemini]       # Google Gemini adapter
pip install privysha[ml]           # ML-enhanced PII (spaCy + transformers)
pip install privysha[integrations] # FastAPI, LangChain, Instructor, etc.
pip install privysha[local-advisor] # PrivyFit catalog fetch
pip install privysha[all]          # All optional dependencies
```

See [integrations.md](integrations.md) for the full extras table.

### Verify

```python
from privysha import process
print(process("Hello world"))
```

---

## Your first prompt

### Drop-in processing (recommended)

```python
from privysha import process

result = process(
    "My email is john@gmail.com. Analyze this dataset.",
    return_metrics=True,
)
print(result["optimized"])
print(f"Token reduction: {result['token_reduction']}%")
print(f"PII masked: {result.get('pii_masked', False)}")
```

By default, `process()` returns a **string**. Pass `return_metrics=True` for a dict.

### Wrap an existing LLM client

```python
from privysha import wrap_llm
import openai

client = openai.OpenAI()
secure_client = wrap_llm(client)

response = secure_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "My email is john@gmail.com"}],
)
```

Requires `pip install privysha[openai]` and `OPENAI_API_KEY`.

---

## Processing modes

```python
process(prompt, mode="balanced")  # default — security + optimization
process(prompt, mode="strict")    # maximum PII masking
process(prompt, mode="lite")      # minimal processing, lower latency
process(prompt, mode="off")       # passthrough (no modification)
```

Modes are implemented via `PolicyConfig` presets. See [core-concepts.md](core-concepts.md).

---

## PII detection modes

```python
process(prompt, pii_mode="rule")    # default — lightweight, no downloads
process(prompt, pii_mode="hybrid")  # rules + ML (requires privysha[ml])
process(prompt, pii_mode="ml_only") # experimental ML-only
```

---

## CLI tool

The CLI uses subcommands — not all flags on the default command.

```bash
# Process a prompt
privysha "My email is john@gmail.com. Analyze this dataset."

# With debug metrics
privysha "prompt" --debug

# Built-in test suite
privysha quick-test

# Example prompts
privysha examples

# Benchmarks
privysha benchmark --save

# Local model recommendations (PrivyFit)
privysha recommend --prompt "Analyze dataset" --gpu "RTX 4090"
```

---

## Agent (pipeline + LLM)

For end-to-end prompt processing and LLM generation:

```python
from privysha import Agent

# No API key needed for mock adapter
agent = Agent(model="mock", privacy=True)
response = agent.run("Analyze this dataset with john@example.com")
print(response)

# With tracing
result = agent.run("prompt", trace=True)
print(result["prompts"]["optimized"])
print(result["response"])
```

Supported `Agent` constructor parameters:

| Parameter | Description |
|-----------|-------------|
| `model` | Model name (default: `gpt-4o-mini`) |
| `privacy` | Enable privacy features (default: `True`) |
| `token_budget` | Token budget for optimization (default: `1200`) |
| `provider` | Provider override (auto-detected if omitted) |
| `fallback_providers` | List of fallback provider configs |
| `routing_config` | Smart routing configuration dict |
| `local_model` | Set to `"auto"` for PrivyFit model selection |
| `sample_prompts` | Prompt corpus for PrivyFit when `local_model="auto"` |

`Agent.run(prompt, trace=False, task_type="chat")` returns a **string** unless `trace=True`.

---

## API keys (optional)

Basic `process()` / `sanitize()` work without API keys. For LLM adapters:

```bash
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export GOOGLE_API_KEY=your_key
```

---

## Next steps

1. [Core Concepts](core-concepts.md) — understand modes and pipeline
2. [API Reference](api-reference.md) — full function signatures
3. [Security](security.md) — PII masking and fail-closed mode
4. [Local Model Advisor](local-advisor.md) — PrivyFit recommendations
