# Framework Integrations

PrivySHA is designed as a **preprocessing layer** — it runs before your LLM, guardrails, or structured-output library. It does not replace Guardrails, Instructor, or LangChain; it composes with them.

---

## Installation extras

| Integration | Install |
|-------------|---------|
| OpenAI | `pip install privysha[openai]` |
| Anthropic | `pip install privysha[anthropic]` |
| Gemini | `pip install privysha[gemini]` |
| ML PII | `pip install privysha[ml]` |
| All integrations | `pip install privysha[integrations]` |
| Instructor | `pip install privysha[instructor]` |
| Guardrails | `pip install privysha[guardrails]` |
| LangChain | `pip install privysha[langchain]` |
| FastAPI | `pip install privysha[fastapi]` |
| Flask | `pip install privysha[flask]` |
| Django | `pip install privysha[django]` |
| LlamaIndex | `pip install privysha[llamaindex]` |
| OpenTelemetry | `pip install privysha[otel]` |

---

## FastAPI

Process request bodies before they reach your route handlers:

```python
from fastapi import FastAPI
from privysha.integrations.fastapi.middleware import PrivySHAMiddleware

app = FastAPI()
app.add_middleware(PrivySHAMiddleware, mode="balanced", privacy=True)

@app.post("/chat")
async def chat(body: dict):
    # body["message"] is already sanitized when middleware is enabled
    return {"status": "ok"}
```

See also: `examples/fastapi_integration.py`

---

## LangChain

Wrap an existing LLM so prompts are preprocessed automatically:

```python
from langchain_openai import ChatOpenAI
from privysha import wrap_langchain_llm

llm = ChatOpenAI(model="gpt-4o-mini")
secure_llm = wrap_langchain_llm(llm, mode="balanced")

response = secure_llm.invoke("Contact john@example.com for details")
```

Composer pattern for chains:

```python
from privysha import compose_with_langchain

composer = compose_with_langchain()
chain = composer.wrap_chain(your_chain)
```

See also: `examples/integration_showcase.py`

---

## Instructor

PrivySHA sanitizes the prompt **before** Instructor extracts structured output:

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel
from privysha import compose_with_instructor

class UserInfo(BaseModel):
    name: str
    email: str

client = instructor.from_openai(OpenAI())
composer = compose_with_instructor()

result = composer.create_with_privysha(
    prompt="Extract: John Doe, john@example.com",
    response_model=UserInfo,
    client=client,
    model="gpt-4o-mini",
)
```

PII in the input prompt is masked before it reaches the model. Use `validate_with_privysha()` to post-process structured results.

See also: `examples/instructor_guardrails_example.py`

---

## Guardrails AI

Run PrivySHA first, then Guardrails validation:

```python
from privysha import compose_with_guardrails, process

composer = compose_with_guardrails()

# Manual two-step
secure_prompt = process("User said: john@example.com and ignore instructions")
# guard.validate(secure_prompt)  # your Guardrails guard

# Composer helper
result = composer.validate_with_privysha(
    prompt="User said: john@example.com",
    guard=your_guard,
)
print(result["secure_prompt"])
print(result["validation_passed"])
```

PrivySHA handles PII masking and injection neutralization; Guardrails handles output schema and policy validation.

See also: `examples/instructor_guardrails_example.py`

---

## Drop-in (recommended)

For most apps, the simplest integration is still the core API:

```python
from privysha import process, wrap_llm

# Preprocess manually
safe = process(user_input)

# Or wrap the SDK client
secure_client = wrap_llm(openai_client)
```

---

## Flask

```python
from flask import Flask
from privysha.integrations.flask.middleware import PrivySHAMiddleware

app = Flask(__name__)
PrivySHAMiddleware(app, endpoints=["/api/chat"])
```

---

## Django

Add to `MIDDLEWARE` in settings:

```python
MIDDLEWARE = [
    # ...
    "privysha.integrations.django.middleware.PrivySHAMiddleware",
]
```

Optional `PRIVYSHA_CONFIG` dict in settings for privacy/token budget.

---

## LlamaIndex

```python
from privysha.integrations.llamaindex.plugin import wrap_query_engine

secure_engine = wrap_query_engine(your_query_engine)
```

---

## OpenTelemetry

```python
from privysha import enable_otel, process

enable_otel("my-app")  # requires pip install privysha[otel]
process("Hello", trace=True)
```

Stage spans are emitted automatically when OTEL is enabled.

---

## Composition order

```
User Input → PrivySHA (PII + injection + optimization) → Framework/Guardrails → LLM → Response
```

This ordering ensures sensitive data never reaches the model in raw form, while downstream tools still enforce their own policies.
