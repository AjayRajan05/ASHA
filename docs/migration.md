# Migration Guide

**Migrating to PrivySHA v0.3.0** from other PII/optimization tools.

---

## From raw regex / manual masking

**Before:**

```python
import re
text = re.sub(r"[\w.+-]+@[\w-]+\.\w+", "[EMAIL]", user_input)
response = openai_client.chat.completions.create(messages=[{"role": "user", "content": text}])
```

**After:**

```python
from privysha import process

safe = process(user_input, mode="strict")
response = openai_client.chat.completions.create(messages=[{"role": "user", "content": safe}])
```

Or wrap the client entirely:

```python
from privysha import wrap_llm
secure_client = wrap_llm(openai_client)
```

---

## From Microsoft Presidio

**Before:**

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
results = analyzer.analyze(text=text, language="en")
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
```

**After:**

```python
from privysha import sanitize

result = sanitize(text, return_details=True, mode="strict")
safe_text = result["sanitized"]
print(result["pii_detected"])
```

For ML-enhanced detection similar to Presidio NER:

```python
sanitize(text, pii_mode="hybrid")  # requires pip install privysha[ml]
```

---

## From spaCy NER

**Before:**

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
# manual entity replacement...
```

**After:**

```python
from privysha import process

safe = process(text, pii_mode="hybrid")  # uses spaCy via privysha[ml]
```

Default `pii_mode="rule"` requires no spaCy download.

---

## From LangChain output parsers / guardrails

PrivySHA composes **before** guardrails and structured output — it preprocesses the prompt:

```python
from privysha import compose_with_guardrails

composer = compose_with_guardrails()
result = composer.validate_with_privysha(prompt=user_message, guard=your_guard)
```

See [integrations.md](integrations.md).

---

## From PrivySHA 0.2.x / 1.0.x

### Version change

The project returned from 1.0.x to **0.3.0 developer preview**. Expect API evolution before stable 1.0.

### Key changes in 0.3.0

- Added `recommend_local_model()` (PrivyFit)
- Added `RoutingStrategy.LOCAL_PRIVACY`
- Added `Agent(local_model="auto")`, `wrap_llm(..., auto_select_local_model=True)`
- PyPI classifier changed to Alpha / developer preview

### Deprecated

- `DebugTracer` → use `TraceContext` via `process(..., trace=True)`

### Unchanged

- `process()`, `wrap_llm()`, `optimize()`, `sanitize()` signatures
- Policy modes: `balanced`, `strict`, `lite`, `off`
- `pii_mode`: `rule`, `hybrid`, `ml_only`

---

## FastAPI integration

```python
from fastapi import FastAPI
from privysha.integrations.fastapi.middleware import PrivySHAMiddleware

app = FastAPI()
app.add_middleware(PrivySHAMiddleware, mode="balanced", privacy=True)
```

Or:

```python
from privysha import add_privysha_to_fastapi, IntegrationConfig

app = add_privysha_to_fastapi(app, IntegrationConfig(mode="balanced"))
```

---

## Validate migration

```bash
privysha quick-test
python benchmarks/run_benchmarks.py --save
python examples/developer_preview_demo.py
```

Compare PII masking:

```python
from privysha import sanitize

result = sanitize(your_test_prompt, return_details=True, mode="strict")
print(result["sanitized"])
print(result["pii_detected"])
assert "@" not in result["sanitized"]  # emails masked
```

---

## Related docs

- [Getting Started](getting-started.md)
- [Versioning](versioning.md)
- [API Reference](api-reference.md)
