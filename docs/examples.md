# Examples

**PrivySHA v0.3.0** — real-world usage patterns.

All examples use the actual public API. See [api-reference.md](api-reference.md) for full signatures.

---

## Basic prompt processing

```python
from privysha import process

# Simple — returns a string
result = process("My email is john@example.com. Analyze this dataset.")
print(result)

# With metrics
result = process("prompt", return_metrics=True)
print(result["optimized"])
print(f"Saved {result['token_reduction']}% tokens")
print(f"PII masked: {result.get('pii_masked', False)}")
```

---

## Wrap OpenAI client

```python
import os
from privysha import wrap_llm
import openai

os.environ["OPENAI_API_KEY"] = "your-key"
client = openai.OpenAI()
secure = wrap_llm(client, mode="balanced")

response = secure.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Analyze data from john@example.com"}],
)
```

Requires `pip install privysha[openai]`.

---

## Security-only sanitization

```python
from privysha import sanitize

safe = sanitize("Contact me at 555-123-4567 or john@company.com")

# With details
result = sanitize("prompt", return_details=True)
print(result["sanitized"])
print(result["pii_detected"])
```

---

## Optimization-only

```python
from privysha import optimize

compressed = optimize(
    "Hey bro can you please thoroughly analyze this entire dataset for me?",
    return_metrics=True,
)
print(compressed["optimized"])
print(f"Reduction: {compressed['token_reduction']}%")
```

---

## Agent with mock adapter (no API key)

```python
from privysha import Agent

agent = Agent(model="mock", privacy=True)
response = agent.run("Analyze this dataset with john@example.com")
print(response)
```

---

## Agent with tracing

```python
from privysha import Agent

agent = Agent(model="mock", privacy=True)
result = agent.run("Analyze dataset with john@example.com", trace=True)

print("Optimized:", result["prompts"]["optimized"])
print("Response:", result["response"])
```

---

## Agent with OpenAI

```python
import os
from privysha import Agent

os.environ["OPENAI_API_KEY"] = "your-key"
agent = Agent(model="gpt-4o-mini", privacy=True)
response = agent.run("Summarize the key trends in this data")
print(response)
```

---

## Agent with fallback providers

```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "ollama", "model": "llama3"},
    ],
)
response = agent.run("Analyze this data")
```

Each fallback provider requires its optional extra and credentials.

---

## Reversible masking

```python
from privysha import sanitize, unmask

result = sanitize(
    "Reply to alice@corp.com about order #12345",
    return_details=True,
    reversible=True,
)

safe_prompt = result["sanitized"]
# Send safe_prompt to LLM...
llm_output = "Confirmed for alice@corp.com"
restored = unmask(llm_output, result["masking_map"])
```

---

## PrivyFit local model recommendation

```python
from privysha import recommend_local_model

report = recommend_local_model(
    prompts=[
        "My email is john@company.com — analyze this dataset.",
        "Write a Python REST API client.",
    ],
    mode="strict",
    gpu="RTX 4090",
    top=3,
)

for model in report.top_models:
    print(model.model_id, model.ollama_pull_name, model.reasoning)
```

---

## FastAPI middleware

```python
from fastapi import FastAPI
from privysha.integrations.fastapi.middleware import PrivySHAMiddleware

app = FastAPI()
app.add_middleware(PrivySHAMiddleware, mode="balanced", privacy=True)
```

See `examples/fastapi_integration.py`.

---

## LangChain wrapper

```python
from langchain_openai import ChatOpenAI
from privysha import wrap_langchain_llm

llm = ChatOpenAI(model="gpt-4o-mini")
secure_llm = wrap_langchain_llm(llm, mode="balanced")
response = secure_llm.invoke("Contact john@example.com")
```

---

## Async processing

```python
import asyncio
from privysha import process_async

async def main():
    result = await process_async(
        "Analyze data with john@example.com",
        mode="balanced",
    )
    print(result)

asyncio.run(main())
```

---

## Benchmarking

```bash
python benchmarks/run_benchmarks.py --save
privysha benchmark --save
```

See [benchmarks.md](benchmarks.md).

---

## Developer preview demo

```bash
pip install -e .
python examples/developer_preview_demo.py
```

Runs `process()` and `recommend_local_model()` with no API keys.

---

## More examples in repo

| File | Description |
|------|-------------|
| `examples/developer_preview_demo.py` | Minimal no-keys demo |
| `examples/fastapi_integration.py` | FastAPI middleware |
| `examples/integration_showcase.py` | Framework integrations |

---

## Related docs

- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [Integrations](integrations.md)
