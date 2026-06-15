# Model Gateway

**PrivySHA v0.4.1** — adapters and client wrapping.

---

## wrap_llm (recommended)

```python
from privysha.integrations import wrap_llm
import openai

client = wrap_llm(openai.OpenAI(), mode="balanced")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Data from john@example.com"}],
)
```

Import from **`privysha.integrations`**, not root.

---

## Providers

| Provider | Extra | Env var |
|----------|-------|---------|
| OpenAI | `privysha[openai]` | `OPENAI_API_KEY` |
| Anthropic | `privysha[anthropic]` | `ANTHROPIC_API_KEY` |
| Gemini | `privysha[gemini]` | `GOOGLE_API_KEY` |
| Grok | — | `GROK_API_KEY` |
| Ollama | — | local server |
| HuggingFace | `privysha[transformers]` | — |
| Mock | — | testing only |

---

## Agent

End-to-end preprocess + generate:

```python
from privysha import Agent

agent = Agent(model="gpt-4o-mini", privacy=True)
response = agent.run("Analyze Q1 sales")
```

Mock adapter (no API key):

```python
agent = Agent(model="mock")
```

---

## AdapterFactory

```python
from privysha.runtime.adapters.factory import AdapterFactory

adapter = AdapterFactory.create(provider="openai", model="gpt-4o-mini")
adapter = AdapterFactory.create(provider="mock")
```

---

## Smart routing

```python
from privysha import Agent

agent = Agent(
    routing_config={
        "chat": "gpt-4o-mini",
        "analysis": "gpt-4o",
    }
)
agent.run("Summarize", task_type="chat")
```

See [routing.md](routing.md).

---

## auto_patch

```python
from privysha.integrations import auto_patch, disable_auto_patch

auto_patch(mode="strict")
disable_auto_patch()
```

Global SDK patch — prefer `wrap_llm()` for production.

---

## Related

- [integrations.md](integrations.md)
- [api-reference.md](api-reference.md)
