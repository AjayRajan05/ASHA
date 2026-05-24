# API Reference

**Core Functions for PrivySHA**

PrivySHA provides 4 main functions that cover all use cases.

---

## 🚀 Core Functions

### 1. process()

Full pipeline processing with security and optimization.

```python
from privysha import process

result = process(
    prompt: str,
    mode: str = "balanced",
    return_metrics: bool = False,
    debug: bool = False,
    verbose: bool = False
) -> Union[str, Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | str | Required | Input prompt to process |
| `mode` | str | `"balanced"` | `"balanced"`, `"strict"`, `"lite"`, `"off"` |
| `return_metrics` | bool | `False` | Return detailed metrics |
| `debug` | bool | `False` | Enable debug information |
| `verbose` | bool | `False` | Enable logging output |
| `security_fail_closed` | bool | `False` | Return blocked placeholder instead of raw PII on total failure |

**Returns:**
- `str` if `return_metrics=False`
- `dict` if `return_metrics=True`

**Fail-safe:** `process()` never raises on pipeline errors — it returns a security-scrubbed fallback (or the original prompt in fail-open mode). Use `debug=True` for `fallback_reason` and `original_error` fields.

**Examples:**

```python
# Basic usage
result = process("My email is john@gmail.com. Analyze this.")

# With metrics
result = process("prompt", return_metrics=True)
print(f"Saved: {result['token_reduction']}%")

# Debug mode
result = process("prompt", debug=True)
print(result["changes"])
```

---

### 2. wrap_llm()

Wrap existing LLM client with PrivySHA protection.

```python
from privysha import wrap_llm

secure_client = wrap_llm(
    client: Any,
    mode: str = "balanced",
    privacy: bool = True
) -> Any
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | Any | Required | LLM client to wrap |
| `mode` | str | `"balanced"` | Processing mode |
| `privacy` | bool | `True` | Enable privacy features |

**Returns:**
- Wrapped client with same interface

**Examples:**

```python
import openai
from privysha import wrap_llm

client = openai.OpenAI()
secure_client = wrap_llm(client)

# Same interface, automatically secured
response = secure_client.chat.completions.create(
    messages=[{"role": "user", "content": "My email is john@gmail.com"}]
)
```

---

### 3. optimize()

Token optimization only (no security processing).

```python
from privysha import optimize

result = optimize(
    prompt: str,
    mode: str = "balanced",
    return_metrics: bool = False
) -> Union[str, Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | str | Required | Input prompt to optimize |
| `mode` | str | `"balanced"` | Optimization level |
| `return_metrics` | bool | `False` | Return optimization metrics |

**Examples:**

```python
# Basic optimization
optimized = optimize("Very long verbose prompt that needs compression")

# With metrics
result = optimize("prompt", return_metrics=True)
print(f"Tokens saved: {result['token_reduction']}")
```

---

### 4. sanitize()

Security processing only (no optimization).

```python
from privysha import sanitize

result = sanitize(
    prompt: str,
    return_details: bool = False,
    reversible: bool = False,
) -> Union[str, Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | str | Required | Input prompt to sanitize |
| `mode` | str | `"balanced"` | Security level |
| `return_details` | bool | `False` | Return security details |
| `reversible` | bool | `False` | Return `masking_map` for post-LLM unmask (opt-in) |

**Examples:**

```python
# Basic sanitization
safe = sanitize("My email is john@gmail.com and phone is 555-1234")

# With details
result = sanitize("prompt", return_details=True)
print(f"PII detected: {len(result['pii_detected'])}")

# Reversible masking (opt-in — use only when you need to restore LLM output)
result = sanitize("Email alice@corp.com", return_details=True, reversible=True)
from privysha import unmask
restored = unmask(llm_output, result["masking_map"])
```

---

## 🛠️ CLI Tool

### privysha command

```bash
privysha "prompt" [options]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug mode |
| `--mode` | Processing mode |
| `--quick-test` | Run quick test suite |
| `--examples` | Show usage examples |

**Examples:**

```bash
# Quick demo
privysha "My email is john@gmail.com. Analyze this dataset."

# Debug mode
privysha "prompt" --debug

# Quick test
privysha --quick-test
```

---

## 📊 Response Formats

### process() with return_metrics=True

```python
{
    "optimized": "processed_prompt",
    "original": "original_prompt",
    "token_reduction": 45,
    "security_result": {
        "is_safe": True,
        "masked_entities": ["email"],
        "threats_blocked": 0
    },
    "metrics": {
        "tokens_saved": 64,
        "cost_reduction": "47%",
        "processing_time_ms": 54
    }
}
```

### optimize() with return_metrics=True

```python
{
    "optimized": "optimized_prompt",
    "original": "original_prompt",
    "token_reduction": 35,
    "metrics": {
        "tokens_saved": 50,
        "compression_ratio": 0.65
    }
}
```

### sanitize() with return_details=True

```python
{
    "sanitized": "sanitized_prompt",
    "original": "original_prompt",
    "is_safe": True,
    "pii_detected": [
        {"type": "email", "value": "john@gmail.com", "masked": "[EMAIL]_abc123"}
    ],
    "threats_blocked": 0
}
```

---

## ⚙️ Configuration

### Global Configuration

```python
from privysha import configure

configure(
    default_mode="balanced",
    token_budget=1200,
    privacy=True,
    debug=False
)
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PRIVYSHA_MODE` | Default processing mode |
| `PRIVYSHA_DEBUG` | Enable debug mode |
| `PRIVYSHA_TOKEN_BUDGET` | Default token budget |

---

## 🔧 Advanced Usage

### Async Support

```python
from privysha import process_async, optimize_async, sanitize_async

result = await process_async("prompt")
result = await optimize_async("prompt")
result = await sanitize_async("prompt")
```

### Custom Processing

```python
from privysha import Pipeline

pipeline = Pipeline(
    privacy=True,
    token_budget=1200,
    debug_enabled=False
)

result = pipeline.process("prompt")
```

---

## 🚨 Error Handling

PrivySHA uses fail-safe design - always returns usable results.

```python
try:
    result = process("prompt")
except Exception as e:
    # Falls back to original prompt
    print(f"Processing failed: {e}")
    # result is still usable
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ImportError` | Missing dependencies | Install required packages |
| `ConnectionError` | LLM API unavailable | Use fallback or offline mode |
| `ValidationError` | Invalid parameters | Check function signatures |

---

## 📈 Performance Metrics

When `return_metrics=True`, PrivySHA provides detailed performance data:

- **Token Reduction**: Percentage of tokens saved
- **Cost Savings**: Estimated cost reduction
- **Processing Time**: Time taken for processing
- **PII Detected**: Number of PII items found
- **Threats Blocked**: Security threats neutralized

These metrics help you optimize your LLM usage and ensure security compliance. 
        "model": "gpt-3.5-turbo",
        "config": {"timeout": 30}
    }
]
```

#### Custom Routing Strategy

```python
def custom_routing(task_ir, context):
    if task_ir.intent == "analyze":
        return {"provider": "openai", "model": "gpt-4o"}
    else:
        return {"provider": "anthropic", "model": "claude-3-haiku"}

agent = Agent(routing_strategy=custom_routing)
```

#### Methods

##### run()

```python
result = agent.run(
    prompt="Analyze data",
    trace=False,
    context=None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | str | Required | The input prompt to process |
| `trace` | bool | `False` | Enable full pipeline tracing |
| `context` | list | `None` | Conversation context for multi-turn conversations |

**Returns:**

```python
{
    "response": "The data shows...",
    "metadata": {
        "model_used": "gpt-4o-mini",
        "provider": "openai",
        "tokens_used": 45,
        "processing_time_ms": 1234
    },
    "optimization_metrics": {
        "original_tokens": 120,
        "optimized_tokens": 38,
        "reduction_percentage": 68.3
    },
    "security_result": {
        "pii_detected": [],
        "pii_masked": 0,
        "injection_attempts": 0
    }
}
```

##### print_debug_trace()

```python
agent.print_debug_trace()
```

Prints the most recent debug trace to console.

##### get_stats()

```python
stats = agent.get_stats()
```

Returns performance and usage statistics.

---

## 🧠 Prompt IR Classes

### PromptIR

Structured representation of user intent.

#### Constructor

```python
from privysha.ir.prompt_ir import PromptIR

ir = PromptIR({
    "intent": "analyze",
    "object": "data",
    "constraints": ["thorough"],
    "style": "analytical"
})
```

#### Properties

| Property | Type | Description |
|-----------|------|-------------|
| `intent` | str | Primary user intent |
| `object` | str | Object the intent acts upon |
| `constraints` | list | List of constraints |
| `style` | str | Desired output style |
| `privacy` | dict | Privacy configuration |
| `metadata` | dict | Additional metadata |

#### Methods

##### is_valid()

```python
valid = ir.is_valid()
```

Returns `True` if IR structure is valid.

##### to_dict()

```python
data = ir.to_dict()
```

Returns IR as dictionary.

##### from_prompt()

```python
ir = PromptIR.from_prompt("Analyze data thoroughly")
```

Creates IR from natural language prompt.

---

### IRBuilder

Builds PromptIR from text.

#### Constructor

```python
from privysha.ir.ir_builder import IRBuilder

builder = IRBuilder(
    confidence_threshold=0.8,
    custom_intents={},
    custom_constraints=[]
)
```

#### Methods

##### generate()

```python
ir = builder.generate(
    prompt="Analyze data",
    context=None
)
```

##### add_intent_pattern()

```python
builder.add_intent_pattern(
    name="visualize",
    patterns=["plot", "chart", "graph", "visualize"]
)
```

##### add_constraint_pattern()

```python
builder.add_constraint_pattern(
    name="gdpr_compliant",
    patterns=["gdpr", "privacy", "compliant"]
)
```

---

## 🔒 Security Classes

### SecurityLayer

Handles PII detection and injection protection.

#### Constructor

```python
from privysha.security.security_layer import SecurityLayer

security = SecurityLayer(
    security_level="medium",
    custom_pii_patterns={},
    custom_injection_rules=[]
)
```

#### Security Levels

| Level | Description | Features |
|-------|-------------|----------|
| `"low"` | Basic protection | Basic PII masking |
| `"medium"` | Standard protection | PII + basic injection |
| `"high"` | Enhanced protection | Comprehensive security |
| `"strict"` | Maximum protection | All security features |

#### Methods

##### scan()

```python
result = security.scan(text="Contact john@email.com")
```

**Returns:**

```python
{
    "pii_detected": ["email"],
    "pii_masked": 1,
    "masked_text": "Contact [EMAIL]",
    "injection_attempts": 0,
    "risk_level": "medium"
}
```

##### add_pii_pattern()

```python
security.add_pii_pattern(
    name="employee_id",
    pattern=r"EMP\d{6}",
    replacement="[EMPLOYEE_ID]"
)
```

##### add_injection_rule()

```python
security.add_injection_rule(
    name="custom_attack",
    pattern=r"(ignore|forget).+(above|previous)",
    action="block"
)
```

---

## ⚡ Optimization Classes

### PromptOptimizer

Optimizes prompts for token reduction.

#### Constructor

```python
from privysha.compiler.optimizer_engine import PromptOptimizer

optimizer = PromptOptimizer(
    level="balanced",
    preserve_semantics=True,
    target_reduction=0.5
)
```

#### Methods

##### optimize()

```python
result = optimizer.optimize(ir)
```

**Returns:**

```python
{
    "optimized_ir": {...},
    "original_tokens": 120,
    "optimized_tokens": 38,
    "reduction_percentage": 68.3,
    "optimizations_applied": [
        "constraint_consolidation",
        "object_simplification"
    ]
}
```

##### add_optimization_rule()

```python
optimizer.add_optimization_rule(
    name="custom_compression",
    pattern=r"(very|quite|rather)\s+(\w+)",
    replacement=r"\2",
    confidence=0.8
)
```

---

## 🌐 Gateway Classes

### ModelRouter

Routes requests to appropriate models.

#### Constructor

```python
from privysha.routing.model_router import ModelRouter

router = ModelRouter(
    strategy="balanced",
    fallback_providers=[],
    cost_limits={}
)
```

#### Routing Strategies

| Strategy | Description |
|----------|-------------|
| `"cost_optimized"` | Minimize cost |
| `"performance_optimized"` | Maximize performance |
| `"balanced"` | Balance cost and performance |
| `custom_function` | Custom routing logic |

#### Methods

##### route()

```python
selection = router.route(
    task_ir=ir,
    context={}
)
```

**Returns:**

```python
{
    "provider": "openai",
    "model": "gpt-4o-mini",
    "reasoning": "Balanced choice for analysis task",
    "confidence": 0.92
}
```

##### add_routing_rule()

```python
router.add_routing_rule(
    condition="intent == 'analyze' and complexity > 0.7",
    action={"provider": "openai", "model": "gpt-4o"},
    priority=1
)
```

---

## 🔧 Adapters

### BaseAdapter

Base class for all model adapters.

#### Methods

##### generate()

```python
response = adapter.generate(prompt="Analyze data")
```

##### validate_config()

```python
valid = adapter.validate_config()
```

### OpenAIAdapter

OpenAI model adapter.

#### Constructor

```python
from privysha.adapters.openai_adapter import OpenAIAdapter

adapter = OpenAIAdapter(
    model="gpt-4o-mini",
    api_key="your_key",
    base_url=None,
    timeout=30
)
```

### AnthropicAdapter

Anthropic Claude adapter.

#### Constructor

```python
from privysha.adapters.claude_adapter import ClaudeAdapter

adapter = ClaudeAdapter(
    model="claude-3-haiku",
    api_key="your_key",
    timeout=30
)
```

### GeminiAdapter

Google Gemini adapter.

#### Constructor

```python
from privysha.adapters.gemini_adapter import GeminiAdapter

adapter = GeminiAdapter(
    model="gemini-1.5-flash",
    api_key="your_key",
)
```

### OllamaAdapter

Local Ollama adapter (no API key required).

#### Constructor

```python
from privysha.adapters.ollama_adapter import OllamaAdapter

adapter = OllamaAdapter(
    model="llama3",
    base_url="http://localhost:11434",
)
```

### GrokAdapter

xAI Grok adapter.

#### Constructor

```python
from privysha.adapters.grok_adapter import GrokAdapter

adapter = GrokAdapter(
    model="grok-beta",
    api_key="your_key",
)
```

### AdapterFactory

Create adapters by provider name:

```python
from privysha import AdapterFactory

adapter = AdapterFactory.create(provider="openai", model="gpt-4o-mini")
```

Supported providers: `openai`, `anthropic`, `gemini`, `ollama`, `huggingface`, `grok`, `mock`.

### HuggingFaceAdapter

Local HuggingFace model adapter.

#### Constructor

```python
from privysha.adapters.hf_adapter import HuggingFaceAdapter

adapter = HuggingFaceAdapter(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    device="auto",
    torch_dtype="float16"
)
```

---

## 🔌 Framework Integrations

PrivySHA composes with existing frameworks — it preprocesses prompts **before** they reach guardrails or structured-output libraries.

### FastAPI

```python
from fastapi import FastAPI
from privysha.integrations.fastapi.middleware import PrivySHAMiddleware

app = FastAPI()
app.add_middleware(PrivySHAMiddleware, mode="balanced")
```

Or use the helper:

```python
from privysha import add_privysha_to_fastapi

app = add_privysha_to_fastapi(app, mode="strict")
```

### LangChain

```python
from privysha import wrap_langchain_llm, LangChainPromptTemplate

secure_llm = wrap_langchain_llm(your_llm)
template = LangChainPromptTemplate.from_template("Analyze {input}")
```

### Instructor

```python
from privysha import compose_with_instructor, PrivySHAInstructorClient

composer = compose_with_instructor()
# Preprocesses prompt before Instructor structured output call
result = composer.create_with_privysha(
    prompt="Extract user from john@example.com",
    response_model=UserInfo,
    client=instructor_client,
)
```

Optional: `pip install instructor`

### Guardrails AI

```python
from privysha import compose_with_guardrails

composer = compose_with_guardrails()
result = composer.validate_with_privysha(
    prompt="User message with PII",
    guard=your_guardrails_guard,
)
```

See **[Integrations Guide](integrations.md)** for full examples.

---

## 🏗️ Pipeline Classes

### Pipeline

Main processing pipeline.

#### Constructor

```python
from privysha.pipeline import Pipeline

pipeline = Pipeline(
    privacy=True,
    token_budget=1200,
    security_level="MEDIUM",
    debug_enabled=False,
    fallback_mode=True,
    timeout_ms=0,
    pii_mode="rule",
)
```

#### Methods

##### process()

```python
result = pipeline.process(
    prompt="Analyze data",
    config={}
)
```

##### add_stage()

```python
pipeline.add_stage(
    name="custom_stage",
    stage_instance=CustomStage(),
    position=3
)
```

##### configure()

```python
pipeline.configure({
    "optimization_level": "aggressive",
    "security_level": "high"
})
```

---

## 🔍 Debugging Classes

### PrivySHADebugger

Debugging and tracing utilities.

#### Constructor

```python
from privysha.debug.debugger import PrivySHADebugger

debugger = PrivySHADebugger(
    enabled=True,
    log_level="debug",
    output_file="debug.log"
)
```

#### Methods

##### trace()

```python
trace_data = debugger.trace(
    stage="optimization",
    input_data={},
    output_data={},
    metadata={}
)
```

##### generate_report()

```python
report = debugger.generate_report(
    format="html",
    include_charts=True
)
```

---

## 📊 Utility Functions

### Metrics

```python
from privysha.utils.metrics import calculate_metrics

metrics = calculate_metrics(
    original_prompt="Analyze comprehensive data",
    optimized_prompt="Analyze data",
    response_time_ms=1234,
    tokens_used=45
)
```

### Validation

```python
from privysha.utils.validation import validate_prompt

validation = validate_prompt(
    prompt="Analyze data",
    checks=["length", "content", "security"]
)
```

### Configuration

```python
from privysha.utils.config import load_config

config = load_config(
    file_path="config.yaml",
    environment="production"
)
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | None |
| `ANTHROPIC_API_KEY` | Anthropic API key | None |
| `GROK_API_KEY` | xAI API key | None |
| `PRIVYSHA_LOG_LEVEL` | Logging level | `"INFO"` |
| `PRIVYSHA_CACHE_DIR` | Cache directory | `"./cache"` |
| `PRIVYSHA_CONFIG_FILE` | Config file path | `"./config.yaml"` |

### Configuration File

```yaml
# config.yaml
privysha:
  model: "gpt-4o-mini"
  privacy: true
  optimization_level: "balanced"
  
  security:
    level: "medium"
    pii_detection: true
    injection_protection: true
    
  routing:
    strategy: "balanced"
    fallback_providers:
      - provider: "anthropic"
        model: "claude-3-haiku"
        
  optimization:
    target_reduction: 0.5
    preserve_semantics: true
    
  debugging:
    enabled: false
    log_level: "INFO"
```

---

## 🚨 Error Handling

### Exception Classes

```python
from privysha.exceptions import (
    PrivySHAError,
    ConfigurationError,
    ModelError,
    SecurityError,
    OptimizationError
)

try:
    result = agent.run("Analyze data")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ModelError as e:
    print(f"Model error: {e}")
except SecurityError as e:
    print(f"Security error: {e}")
except PrivySHAError as e:
    print(f"General error: {e}")
```

### Error Types

| Error | Description |
|--------|-------------|
| `ConfigurationError` | Invalid configuration |
| `ModelError` | Model-related errors |
| `SecurityError` | Security-related errors |
| `OptimizationError` | Optimization failures |
| `ValidationError` | Input validation errors |
| `RoutingError` | Routing failures |

---

## 🎯 Examples

### Basic Usage

```python
from privysha import Agent

# Simple agent
agent = Agent(model="gpt-4o-mini")
response = agent.run("Analyze data")
print(response)
```

### Advanced Usage

```python
from privysha import Agent

# Advanced configuration
agent = Agent(
    model="auto",
    privacy=True,
    optimization_level="aggressive",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"}
    ],
    routing_strategy="cost_optimized"
)

# Run with tracing
result = agent.run("Analyze comprehensive data", trace=True)

# Access detailed results
print("Response:", result["response"])
print("Optimization:", result["optimization_metrics"])
print("Security:", result["security_result"])

# Print debug trace
agent.print_debug_trace()
```

### Custom Components

```python
from privysha import Agent
from privysha.ir.ir_builder import IRBuilder
from privysha.security.security_layer import SecurityLayer

# Custom IR builder
builder = IRBuilder()
builder.add_intent_pattern("visualize", ["plot", "chart"])

# Custom security
security = SecurityLevel("high")
security.add_pii_pattern("custom_id", r"ID\d{6}")

# Agent with custom components
agent = Agent(
    model="gpt-4o-mini",
    ir_builder=builder,
    security_layer=security
)
```

---

## 🎯 Next Steps

Now that you have the complete API reference:

1. **[See Examples](examples.md)** - Real-world usage
2. **[Check FAQ](faq.md)** - Common questions
3. **[Learn Contributing](contributing.md)** - How to contribute
4. **[Review Roadmap](roadmap.md)** - Future features

---

*Ready to see real-world examples? Check out the [Examples documentation](examples.md)!*
