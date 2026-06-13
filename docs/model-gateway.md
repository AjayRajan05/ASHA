# Model Gateway

**PrivySHA v0.3.0** — connecting to LLM providers via adapters and wrappers.

This doc covers the **actual** provider integration patterns. For routing logic, see [routing.md](routing.md).

---

## wrap_llm() — recommended pattern

Wrap any LLM client so outgoing prompts are preprocessed automatically:

```python
from privysha import wrap_llm
import openai

client = openai.OpenAI()
secure = wrap_llm(client, mode="balanced", privacy=True)

response = secure.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Analyze data from john@example.com"}],
)
```

Works with OpenAI, Anthropic, and generic clients via `UniversalWrapper`.

---

## Provider setup

### OpenAI

```bash
pip install privysha[openai]
export OPENAI_API_KEY=your_key
```

```python
from privysha import wrap_llm
import openai

secure = wrap_llm(openai.OpenAI())
```

### Anthropic

```bash
pip install privysha[anthropic]
export ANTHROPIC_API_KEY=your_key
```

```python
from privysha import wrap_llm
import anthropic

secure = wrap_llm(anthropic.Anthropic())
```

### Google Gemini

```bash
pip install privysha[gemini]
export GOOGLE_API_KEY=your_key
```

### Ollama (local)

No API key required. Requires running Ollama server:

```bash
ollama serve
ollama pull llama3
```

```python
from privysha import Agent

agent = Agent(model="llama3", provider="ollama")
response = agent.run("Analyze this data")
```

### HuggingFace (local)

```bash
pip install privysha[transformers]
```

```python
from privysha import Agent

agent = Agent(model="mistralai/Mistral-7B-Instruct-v0.2")
response = agent.run("Analyze this data")
```

### Mock (testing)

No external services:

```python
from privysha import Agent

agent = Agent(model="mock")
response = agent.run("Test prompt with john@example.com")
```

---

## AdapterFactory

Direct adapter creation for custom integrations:

```python
from privysha import AdapterFactory

adapter = AdapterFactory.create(provider="openai", model="gpt-4o-mini")
response = adapter.generate("Analyze this data")

adapter = AdapterFactory.create(provider="mock")
adapter = AdapterFactory.create(provider="ollama", model="llama3")
```

Supported providers: `openai`, `anthropic`, `gemini`, `ollama`, `huggingface`, `grok`, `mock`.

### With fallbacks

```python
adapter = AdapterFactory.create_with_fallbacks(
    primary_provider="openai",
    primary_model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "ollama", "model": "llama3"},
    ],
)
```

### Smart routing

```python
adapter = AdapterFactory.create_smart_routing({
    "analyze": {"provider": "openai", "model": "gpt-4o"},
    "summarize": {"provider": "openai", "model": "gpt-4o-mini"},
})
```

---

## Agent — full pipeline + generation

```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    privacy=True,
    token_budget=1200,
    provider="openai",          # auto-detected if omitted
    fallback_providers=[...],   # optional
    routing_config={...},       # optional smart routing
    local_model="auto",         # PrivyFit auto-select
    sample_prompts=[...],       # for PrivyFit
)

response = agent.run("Analyze this dataset")
result = agent.run("prompt", trace=True)  # full pipeline trace
```

### Agent.from_env()

```python
agent = Agent.from_env()  # reads PRIVYSHA_MODEL, PRIVYSHA_TOKEN_BUDGET
```

---

## auto_patch (experimental)

Monkey-patch OpenAI/Anthropic SDKs to preprocess prompts globally:

```python
from privysha import auto_patch, get_patch_status, disable_auto_patch

auto_patch()
print(get_patch_status())
disable_auto_patch()
```

May change before 1.0.

---

## auto_select_local_model

```python
from privysha import wrap_llm

secure = wrap_llm(
    ollama_client,
    auto_select_local_model=True,
    sample_prompts=["Analyze dataset with PII."],
)
```

Uses PrivyFit to pick a local model. See [local-advisor.md](local-advisor.md).

---

## Environment variables

| Variable | Provider |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic |
| `GOOGLE_API_KEY` | Gemini |
| `GROK_API_KEY` | Grok |

---

## What process() does NOT do

`process()` preprocesses prompts — it does **not** call LLM APIs. It has no `model`, `provider`, or routing parameters.

For end-to-end prompt → LLM → response, use `Agent` or `wrap_llm()`.

---

## Related docs

- [Routing](routing.md) — model selection strategies
- [Local Model Advisor](local-advisor.md) — PrivyFit
- [Integrations](integrations.md) — framework wrappers
- [API Reference](api-reference.md)
