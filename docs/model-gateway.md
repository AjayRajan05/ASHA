# LLM Provider Support

**Universal compatibility with all major LLM providers**

PrivySHA works with any LLM provider through a simple, unified interface.

---

## 🌐 Supported Providers

### OpenAI
```python
from privysha import wrap_llm
import openai

client = openai.OpenAI()
secure_client = wrap_llm(client)

response = secure_client.chat.completions.create(
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

**Available Models:**
- `gpt-4o` - Most capable
- `gpt-4o-mini` - Fast, cost-effective
- `gpt-4-turbo` - Balanced performance
- `gpt-3.5-turbo` - Basic tasks

### Anthropic Claude
```python
from privysha import wrap_llm
import anthropic

client = anthropic.Anthropic()
secure_client = wrap_llm(client)

response = secure_client.messages.create(
    model="claude-3-haiku",
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

**Available Models:**
- `claude-3-opus` - Most capable
- `claude-3-sonnet` - Balanced
- `claude-3-haiku` - Fast, cost-effective

### Google Gemini
```python
from privysha import wrap_llm
import google.generativeai as genai

genai.configure(api_key="your-api-key")
client = genai.GenerativeModel('gemini-1.5-flash')
secure_client = wrap_llm(client)

response = secure_client.generate_content("Your prompt")
```

**Available Models:**
- `gemini-1.5-pro` - Most capable
- `gemini-1.5-flash` - Fast, cost-effective
- `gemini-1.0-pro` - Legacy support

### HuggingFace (Local)
```python
from privysha import wrap_llm
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("model-name")
tokenizer = AutoTokenizer.from_pretrained("model-name")
secure_client = wrap_llm((model, tokenizer))

response = secure_client.generate("Your prompt")
```

**Available Models:**
- Any HuggingFace model
- Local model files
- Custom trained models

### Ollama (Local)
```python
from privysha import wrap_llm
import ollama

client = ollama.Client()
secure_client = wrap_llm(client)

response = secure_client.generate(
    model="llama3",
    prompt="Your prompt"
)
```

**Available Models:**
- `llama3` - Meta's latest
- `codellama` - Code specialized
- `mistral` - High performance
- Any custom Ollama model

---

## 🔧 Universal Adapter

### Base Adapter Interface

```python
from privysha.adapters import BaseAdapter

class CustomAdapter(BaseAdapter):
    def generate(self, prompt, **kwargs):
        # Custom implementation
        pass
    
    def validate_config(self, config):
        # Validate configuration
        pass
```

### Adding New Providers

```python
from privysha import register_adapter

# Register custom adapter
register_adapter("custom_provider", CustomAdapter)

# Use it
from privysha import process

result = process("prompt", provider="custom_provider")
```

---

## 🎯 Provider Selection

### Automatic Detection

```python
from privysha import process

# Automatically detects provider from model name
result = process("prompt", model="gpt-4o-mini")  # OpenAI
result = process("prompt", model="claude-3-haiku")  # Anthropic
result = process("prompt", model="gemini-1.5-flash")  # Gemini
```

### Manual Specification

```python
from privysha import process

result = process(
    "prompt",
    provider="openai",
    model="gpt-4o-mini"
)
```

---

## 🔄 Fallback Support

### Multiple Providers

```python
from privysha import process

result = process(
    "prompt",
    providers=[
        {"provider": "openai", "model": "gpt-4o-mini"},
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "google", "model": "gemini-1.5-flash"}
    ]
)
```

### Automatic Failover

If primary provider fails, PrivySHA automatically tries the next available provider.

---

## 📊 Provider Comparison

| Provider | Speed | Cost | Quality | Privacy |
|----------|-------|------|---------|---------|
| OpenAI | Fast | Medium | Excellent | Cloud |
| Anthropic | Fast | High | Excellent | Cloud |
| Google | Fast | Medium | Very Good | Cloud |
| HuggingFace | Variable | Free | Variable | Local |
| Ollama | Medium | Free | Good | Local |

---

## 🔑 API Keys Setup

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY=your_openai_key

# Anthropic
export ANTHROPIC_API_KEY=your_anthropic_key

# Google
export GOOGLE_API_KEY=your_google_key
```

### Configuration File

```python
from privysha import configure

configure(
    providers={
        "openai": {"api_key": "your_key"},
        "anthropic": {"api_key": "your_key"},
        "google": {"api_key": "your_key"}
    }
)
```

---

## 🚀 Performance Optimization

### Provider Selection

```python
from privysha import process

# Cost-optimized
result = process("prompt", optimize_for="cost")

# Speed-optimized
result = process("prompt", optimize_for="speed")

# Quality-optimized
result = process("prompt", optimize_for="quality")
```

### Load Balancing

```python
from privysha import process

# Distribute load across providers
result = process(
    "prompt",
    load_balance=True,
    providers=["openai", "anthropic", "google"]
)
```

---

## 🔍 Provider Debugging

### Provider Information

```python
from privysha import get_provider_info

info = get_provider_info("openai")
print(info)
# Output: {"models": [...], "features": [...], "pricing": {...}}
```

### Connection Testing

```python
from privysha import test_provider

result = test_provider("openai")
print(result)
# Output: {"status": "healthy", "latency": 45, "models": [...]}
```

---

## 🎯 Best Practices

### 1. Use Environment Variables

```bash
export OPENAI_API_KEY=your_key
# Instead of hardcoding in code
```

### 2. Set Up Fallbacks

```python
result = process(
    "prompt",
    providers=["openai", "anthropic", "google"]
)
```

### 3. Monitor Provider Health

```python
from privysha import monitor_providers

monitor_providers()  # Alerts on issues
```

### 4. Optimize for Your Use Case

```python
# For cost-sensitive applications
result = process("prompt", optimize_for="cost")

# For speed-critical applications
result = process("prompt", optimize_for="speed")
```

---

## 📋 Provider Summary

PrivySHA provides:

- ✅ **Universal Support**: All major LLM providers
- ✅ **Automatic Detection**: Smart provider selection
- ✅ **Fallback Support**: Reliable operation
- ✅ **Performance Optimization**: Cost/speed/quality tradeoffs
- ✅ **Easy Integration**: Drop-in wrapper functionality
- ✅ **Local Options**: Privacy-preserving local models

Use any LLM provider with the same simple API and get automatic security and optimization.

agent = Agent(model="mistralai/Mistral-7B-Instruct-v0.2")
# Uses local HuggingFace model
```

**Available Models:**
- Any HuggingFace model identifier
- Requires `transformers` library

### Ollama (Local)
```python
from privysha import Agent

agent = Agent(model="llama2")
# Uses local Ollama instance
```

**Available Models:**
- Any model available in Ollama
- Requires Ollama server running

---

## 🔧 Provider Configuration

### API Keys

Set environment variables:

```bash
# OpenAI
export OPENAI_API_KEY=your_openai_key

# Anthropic
export ANTHROPIC_API_KEY=your_anthropic_key

# xAI
export GROK_API_KEY=your_grok_key
```

### Custom Endpoints

```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    provider_config={
        "base_url": "https://api.openai.com/v1",
        "timeout": 30,
        "max_retries": 3
    }
)
```

### Provider-Specific Settings

```python
# OpenAI configuration
agent = Agent(
    model="gpt-4o-mini",
    provider="openai",
    provider_config={
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
)

# Anthropic configuration
agent = Agent(
    model="claude-3-haiku",
    provider="anthropic",
    provider_config={
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_k": 250,
        "top_p": 0.9
    }
)
```

---

## 🔄 Fallback System

### Basic Fallbacks

```python
from privysha import Agent

agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "openai", "model": "gpt-3.5-turbo"}
    ]
)

# If gpt-4o-mini fails, tries claude-3-haiku
# If that fails, tries gpt-3.5-turbo
```

### Fallback Triggers

Fallbacks are triggered by:
- **API errors** (rate limits, downtime)
- **Timeouts** (slow responses)
- **Model unavailable** (deprecation, capacity)
- **Cost thresholds** (exceeds budget)

### Custom Fallback Logic

```python
from privysha import Agent

def custom_fallback_strategy(error, attempt):
    if "rate_limit" in str(error):
        return {"provider": "anthropic", "model": "claude-3-haiku"}
    elif "timeout" in str(error):
        return {"provider": "openai", "model": "gpt-3.5-turbo"}
    else:
        return None  # Use default fallback

agent = Agent(
    model="gpt-4o-mini",
    fallback_strategy=custom_fallback_strategy
)
```

### Fallback Configuration

```python
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "local", "model": "llama-2-7b"}
    ],
    fallback_config={
        "max_attempts": 3,
        "retry_delay": 1.0,  # seconds
        "exponential_backoff": True,
        "fallback_on_timeout": True,
        "fallback_on_error": True
    }
)
```

---

## 🧠 Intelligent Routing

### Automatic Model Selection

```python
from privysha import Agent

agent = Agent(
    model="auto",  # Let PrivySHA choose
    routing_strategy="cost_optimized"
)

# Automatically selects best model based on:
# - Task complexity
# - Cost constraints
# - Performance requirements
```

### Routing Strategies

#### Cost Optimized
```python
agent = Agent(
    model="auto",
    routing_strategy="cost_optimized"
)

# Prioritizes cheapest models that can handle the task
# Simple tasks → gpt-3.5-turbo
# Complex tasks → gpt-4o-mini
# Very complex → gpt-4o
```

#### Performance Optimized
```python
agent = Agent(
    model="auto",
    routing_strategy="performance_optimized"
)

# Prioritizes fastest, most capable models
# All tasks → best available model
```

#### Balanced
```python
agent = Agent(
    model="auto",
    routing_strategy="balanced"
)

# Balances cost and performance
# Default strategy
```

### Custom Routing Rules

```python
def custom_routing_rules(prompt_ir):
    intent = prompt_ir.get("intent")
    complexity = prompt_ir.get("metadata", {}).get("complexity", "medium")
    
    if intent == "analyze" and complexity == "low":
        return {"provider": "openai", "model": "gpt-3.5-turbo"}
    elif intent == "generate" and complexity == "high":
        return {"provider": "anthropic", "model": "claude-3-opus"}
    elif prompt_ir.get("privacy", {}).get("level") == "high":
        return {"provider": "local", "model": "llama-2-7b"}
    else:
        return {"provider": "openai", "model": "gpt-4o-mini"}

agent = Agent(
    model="auto",
    routing_strategy=custom_routing_rules
)
```

---

## 🔍 Provider Capabilities

### Capability Matrix

| Feature | OpenAI | Anthropic | xAI | HuggingFace | Ollama |
|---------|---------|-----------|------|-------------|---------|
| **Text Generation** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Function Calling** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Streaming** | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| **Vision** | ✅ | ✅ | ❌ | ⚠️ | ❌ |
| **Local Processing** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Fine-tuning** | ✅ | ✅ | ❌ | ✅ | ✅ |

### Provider Selection Guide

#### Use OpenAI when:
- Need function calling
- Want vision capabilities
- Require reliable performance
- Need fine-tuning support

#### Use Anthropic when:
- Need long context
- Want strong reasoning
- Require constitutional AI
- Need good performance

#### Use xAI when:
- Want real-time data
- Need Twitter integration
- Require Grok-specific features

#### Use HuggingFace when:
- Need local processing
- Want custom models
- Require fine-grained control
- Have privacy requirements

#### Use Ollama when:
- Want simple local setup
- Need multiple local models
- Require easy model management

---

## 🛠️ Advanced Configuration

### Load Balancing

```python
agent = Agent(
    model="gpt-4o-mini",
    load_balancing="round_robin",  # round_robin, random, least_used
    provider_instances=[
        {"provider": "openai", "api_key": "key1"},
        {"provider": "openai", "api_key": "key2"},
        {"provider": "openai", "api_key": "key3"}
    ]
)
```

### Rate Limiting

```python
agent = Agent(
    model="gpt-4o-mini",
    rate_limiting={
        "requests_per_minute": 60,
        "tokens_per_minute": 100000,
        "burst_limit": 10
    }
)
```

### Caching

```python
agent = Agent(
    model="gpt-4o-mini",
    caching={
        "enabled": True,
        "ttl": 3600,  # 1 hour
        "max_size": 1000,  # max cached responses
        "cache_key_generator": "prompt_hash"  # prompt_hash, ir_hash
    }
)
```

---

## 🔍 Monitoring & Debugging

### Provider Metrics

```python
result = agent.run("Analyze data", trace=True)

# Provider information
print(result["provider_info"])
# {
#   "provider": "openai",
#   "model": "gpt-4o-mini",
#   "fallback_used": False,
#   "response_time_ms": 1234,
#   "tokens_used": 45,
#   "cost_usd": 0.0012
# }
```

### Performance Analytics

```python
# Get provider performance stats
stats = agent.get_provider_stats()
# {
#   "openai": {
#     "requests": 150,
#     "success_rate": 0.98,
#     "avg_response_time": 1234,
#     "total_cost": 0.45
#   },
#   "anthropic": {
#     "requests": 50,
#     "success_rate": 0.96,
#     "avg_response_time": 2156,
#     "total_cost": 0.38
#   }
# }
```

### Fallback Analytics

```python
# Track fallback usage
fallback_stats = agent.get_fallback_stats()
# {
#   "total_requests": 200,
#   "fallbacks_triggered": 12,
#   "fallback_rate": 0.06,
#   "most_common_fallback": "anthropic->claude-3-haiku",
#   "avg_fallback_time": 2345
# }
```

---

## 🚀 Best Practices

### Production Setup

```python
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "local", "model": "llama-2-7b"}
    ],
    provider_config={
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 1.0
    },
    monitoring={
        "log_requests": True,
        "track_costs": True,
        "alert_on_failures": True
    }
)
```

### Cost Optimization

```python
agent = Agent(
    model="auto",
    routing_strategy="cost_optimized",
    cost_limits={
        "daily_limit_usd": 10.0,
        "monthly_limit_usd": 200.0,
        "alert_threshold": 0.8
    }
)
```

### Privacy Setup

```python
agent = Agent(
    model="local",  # Force local processing
    provider="huggingface",
    privacy_mode="strict",  # No data leaves local environment
    local_models=["llama-2-7b", "mistral-7b"]
)
```

---

## 🎯 Next Steps

Now that you understand the Model Gateway:

1. **[Learn Security Features](security.md)** - PII and injection protection
2. **[Explore Optimization](optimization.md)** - Token reduction techniques
3. **[Check Routing](routing.md)** - Advanced routing strategies
4. **[See Examples](examples.md)** - Gateway in action

---

*Ready to secure your LLM interactions? Check out the [Security documentation](security.md)!*
