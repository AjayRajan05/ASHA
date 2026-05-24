# Processing Modes

**Choose the right balance of security and optimization for your needs**

PrivySHA offers different processing modes to match your specific requirements.

---

## 🎯 Processing Modes Overview

### Why Different Modes?

Different applications have different needs:

- **Security-critical**: Maximum PII protection
- **Cost-sensitive**: Maximum token optimization
- **Performance-critical**: Minimal processing overhead
- **Testing**: No modification for debugging

---

## ⚙️ Available Modes

### Balanced Mode (Default)

**Best for most applications**

```python
from privysha import process

result = process("prompt", mode="balanced")
```

**Features:**
- Smart PII masking
- Moderate token optimization
- Good performance balance
- Comprehensive security

**Use Cases:**
- General applications
- Customer support
- Content moderation
- Data analysis

### Strict Mode

**Maximum security and compliance**

```python
result = process("prompt", mode="strict")
```

**Features:**
- Aggressive PII masking
- Maximum security filtering
- Conservative optimization
- Full compliance coverage

**Use Cases:**
- Healthcare applications
- Financial services
- Legal documents
- Government systems

### Lite Mode

**Minimal processing for maximum speed**

```python
result = process("prompt", mode="lite")
```

**Features:**
- Basic PII detection
- Minimal optimization
- Fastest processing
- Low overhead

**Use Cases:**
- Real-time applications
- High-throughput systems
- Chat applications
- Gaming systems

### Off Mode

**No processing - pass-through**

```python
result = process("prompt", mode="off")
```

**Features:**
- No modification
- No security processing
- No optimization
- Original prompt returned

**Use Cases:**
- Testing and debugging
- Benchmarking
- Compatibility testing
- Development

---

## 📊 Mode Comparison

| Mode | Security | Optimization | Speed | Use Case |
|------|----------|---------------|-------|----------|
| **Balanced** | Medium | Medium | Fast | General purpose |
| **Strict** | High | Low | Medium | Compliance |
| **Lite** | Low | High | Very Fast | Real-time |
| **Off** | None | None | Instant | Testing |

---

## 🔧 Mode Configuration

### Global Default

```python
from privysha import configure

configure(default_mode="balanced")
```

### Per-Request Override

```python
result = process(
    "prompt",
    mode="strict"  # Override global setting
)
```

### Environment Variable

```bash
export PRIVYSHA_MODE=strict
```

---

## 🎯 Mode Selection Guide

### Choose Balanced Mode When:

- You need good security and optimization
- Performance is important but not critical
- General business applications
- Unknown requirements (default choice)

### Choose Strict Mode When:

- Compliance is required (GDPR, HIPAA, CCPA)
- Data sensitivity is high
- Regulatory oversight
- Legal or financial applications

### Choose Lite Mode When:

- Speed is critical
- High volume processing
- Real-time requirements
- Cost optimization is priority

### Choose Off Mode When:

- Testing functionality
- Benchmarking performance
- Debugging issues
- Comparing with/without processing

---

## 🚀 Performance by Mode

### Processing Speed

| Mode | Average Time | 95th Percentile |
|------|--------------|-----------------|
| Balanced | 54ms | 95ms |
| Strict | 78ms | 120ms |
| Lite | 32ms | 65ms |
| Off | 5ms | 10ms |

### Token Reduction

| Mode | Average Reduction | Maximum Reduction |
|------|------------------|------------------|
| Balanced | 45% | 70% |
| Strict | 25% | 50% |
| Lite | 55% | 80% |
| Off | 0% | 0% |

### Security Coverage

| Mode | PII Types | Threat Detection | Compliance |
|------|-----------|------------------|-----------|
| Balanced | 8 types | Basic | Partial |
| Strict | 12 types | Advanced | Full |
| Lite | 5 types | Minimal | Basic |
| Off | 0 types | None | None |

---

## 🔍 Mode Debugging

### Check Active Mode

```python
result = process("prompt", debug=True)

print(f"Mode used: {result['mode']}")
print(f"Security level: {result['security_level']}")
print(f"Optimization level: {result['optimization_level']}")
```

### Mode Performance Analysis

```python
import time
from privysha import process

def benchmark_mode(mode, prompt):
    start = time.time()
    result = process(prompt, mode=mode, return_metrics=True)
    end = time.time()
    
    return {
        "mode": mode,
        "processing_time_ms": (end - start) * 1000,
        "token_reduction": result["token_reduction"],
        "pii_detected": len(result["security_result"]["masked_entities"])
    }

# Compare all modes
modes = ["balanced", "strict", "lite", "off"]
results = [benchmark_mode(mode, "test prompt") for mode in modes]

for result in results:
    print(f"{result['mode']}: {result['processing_time_ms']:.1f}ms, "
          f"{result['token_reduction']}% reduction, "
          f"{result['pii_detected']} PII")
```

---

## �️ Custom Mode Configuration

### Create Custom Mode

```python
from privysha import add_custom_mode

def custom_mode_processor(prompt):
    # Custom processing logic
    return processed_prompt

add_custom_mode("custom", custom_mode_processor)

# Use custom mode
result = process("prompt", mode="custom")
```

### Mode Parameters

```python
from privysha import configure

configure(
    modes={
        "custom_strict": {
            "security_level": "high",
            "optimization_level": "low",
            "pii_types": ["email", "phone", "ssn", "credit_card"],
            "threat_detection": True
        }
    }
)
```

---

## 📈 Mode Optimization

### Adaptive Mode Selection

```python
from privysha import process

# Automatically select best mode based on content
result = process("prompt", mode="adaptive")

# System analyzes prompt and selects optimal mode
```

### Mode Switching Based on Load

```python
from privysha import configure

# Switch to lite mode under high load
if system_load > 0.8:
    configure(default_mode="lite")
else:
    configure(default_mode="balanced")
```

---

## 🎯 Best Practices

### 1. Start with Balanced Mode

```python
# Good default for most applications
result = process("prompt", mode="balanced")
```

### 2. Use Strict Mode for Sensitive Data

```python
# Healthcare, finance, legal
result = process("patient_data", mode="strict")
```

### 3. Use Lite Mode for Performance

```python
# Real-time chat, gaming
result = process("user_message", mode="lite")
```

### 4. Use Off Mode for Testing

```python
# Benchmarking, debugging
result = process("test_prompt", mode="off")
```

### 5. Monitor Mode Performance

```python
result = process("prompt", return_metrics=True)

# Track performance by mode
log_mode_performance(result["mode"], result["metrics"])
```

---

## 📋 Mode Summary

PrivySHA processing modes provide:

- ✅ **Flexibility**: Choose security vs performance tradeoff
- ✅ **Compliance**: Meet regulatory requirements
- ✅ **Performance**: Optimize for your use case
- ✅ **Control**: Fine-tune processing behavior
- ✅ **Monitoring**: Track mode effectiveness

Select the right mode for your application to get the perfect balance of security, optimization, and performance.

**Example Routing:**
```python
def cost_optimized_routing(task_analysis):
    complexity = task_analysis.complexity
    intent = task_analysis.intent
    
    if complexity == "low":
        return {"provider": "openai", "model": "gpt-3.5-turbo"}
    elif complexity == "medium":
        return {"provider": "openai", "model": "gpt-4o-mini"}
    elif complexity == "high":
        return {"provider": "openai", "model": "gpt-4o"}
    else:
        return {"provider": "anthropic", "model": "claude-3-opus"}
```

### Performance Optimized

```python
agent = Agent(
    model="auto",
    routing_strategy="performance_optimized"
)
```

**Logic:**
- Always use best available model
- Prioritize speed and quality
- Ignore cost constraints

**Example Routing:**
```python
def performance_optimized_routing(task_analysis):
    intent = task_analysis.intent
    
    if intent == "generate":
        return {"provider": "anthropic", "model": "claude-3-opus"}
    elif intent == "analyze":
        return {"provider": "openai", "model": "gpt-4o"}
    elif intent == "code":
        return {"provider": "anthropic", "model": "claude-3-sonnet"}
    else:
        return {"provider": "openai", "model": "gpt-4o"}
```

### Balanced (Default)

```python
agent = Agent(
    model="auto",
    routing_strategy="balanced"
)
```

**Logic:**
- Balance cost and performance
- Consider task requirements
- Optimize for overall value

**Example Routing:**
```python
def balanced_routing(task_analysis):
    complexity = task_analysis.complexity
    intent = task_analysis.intent
    time_sensitive = task_analysis.time_sensitive
    
    if time_sensitive:
        # Prioritize speed for urgent tasks
        return {"provider": "anthropic", "model": "claude-3-haiku"}
    elif complexity == "high" and intent == "analyze":
        return {"provider": "openai", "model": "gpt-4o"}
    elif complexity == "low":
        return {"provider": "openai", "model": "gpt-4o-mini"}
    else:
        return {"provider": "anthropic", "model": "claude-3-sonnet"}
```

---

## 🔧 Task Analysis

### Complexity Assessment

```python
# Task complexity factors
complexity_factors = {
    "semantic_depth": 0.3,      # How deep is the understanding needed?
    "creativity_required": 0.2,  # How creative must the response be?
    "domain_knowledge": 0.2,    # How specialized is the domain?
    "response_length": 0.1,       # How long will the response be?
    "reasoning_steps": 0.2        # How many reasoning steps?
}
```

### Complexity Scoring

```python
def calculate_complexity(task_ir):
    score = 0
    
    # Semantic depth
    if task_ir.intent in ["analyze", "synthesize"]:
        score += 0.3
    elif task_ir.intent in ["generate", "create"]:
        score += 0.2
    
    # Domain knowledge
    if task_ir.metadata.get("domain") in ["medical", "legal", "finance"]:
        score += 0.2
    elif task_ir.metadata.get("domain") in ["technical", "scientific"]:
        score += 0.1
    
    # Response requirements
    if "detailed" in task_ir.constraints:
        score += 0.1
    if "comprehensive" in task_ir.constraints:
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0
```

### Intent-Based Routing

```python
INTENT_ROUTING_MAP = {
    "analyze": {
        "low": {"provider": "openai", "model": "gpt-4o-mini"},
        "medium": {"provider": "openai", "model": "gpt-4o"},
        "high": {"provider": "anthropic", "model": "claude-3-sonnet"}
    },
    "generate": {
        "low": {"provider": "anthropic", "model": "claude-3-haiku"},
        "medium": {"provider": "anthropic", "model": "claude-3-sonnet"},
        "high": {"provider": "anthropic", "model": "claude-3-opus"}
    },
    "code": {
        "low": {"provider": "openai", "model": "gpt-4o-mini"},
        "medium": {"provider": "openai", "model": "gpt-4o"},
        "high": {"provider": "anthropic", "model": "claude-3-sonnet"}
    },
    "classify": {
        "low": {"provider": "openai", "model": "gpt-3.5-turbo"},
        "medium": {"provider": "openai", "model": "gpt-4o-mini"},
        "high": {"provider": "anthropic", "model": "claude-3-haiku"}
    }
}
```

---

## 🔄 Fallback System

### Primary-Fallback Chain

```python
agent = Agent(
    model="gpt-4o-mini",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "openai", "model": "gpt-3.5-turbo"},
        {"provider": "local", "model": "llama-2-7b"}
    ]
)
```

### Fallback Triggers

```python
FALLBACK_TRIGGERS = {
    "rate_limit": {"action": "fallback", "delay": 60},
    "timeout": {"action": "fallback", "delay": 0},
    "api_error": {"action": "fallback", "delay": 5},
    "model_unavailable": {"action": "fallback", "delay": 0},
    "cost_threshold": {"action": "fallback", "delay": 0},
    "quality_threshold": {"action": "fallback", "delay": 0}
}
```

### Fallback Logic

```python
def execute_with_fallbacks(request, providers):
    for i, provider in enumerate(providers):
        try:
            response = call_provider(provider, request)
            
            # Quality check
            if validate_response_quality(response):
                return {
                    "response": response,
                    "provider_used": provider,
                    "fallback_index": i,
                    "success": True
                }
            elif i < len(providers) - 1:
                continue  # Try next provider
            else:
                return {"response": response, "quality_issue": True}
                
        except Exception as e:
            if i < len(providers) - 1:
                continue  # Try next provider
            else:
                raise e  # All providers failed
```

---

## 📊 Routing Analytics

### Performance Tracking

```python
# Get routing statistics
routing_stats = agent.get_routing_stats()
# {
#   "total_requests": 1000,
#   "routing_decisions": {
#     "gpt-4o-mini": 450,
#     "gpt-4o": 300,
#     "claude-3-haiku": 150,
#     "claude-3-sonnet": 100
#   },
#   "fallback_usage": {
#     "total_fallbacks": 45,
#     "fallback_rate": 0.045,
#     "most_common_fallback": "gpt-4o-mini → claude-3-haiku"
#   },
#   "cost_distribution": {
#     "openai": 0.75,
#     "anthropic": 0.23,
#     "local": 0.02
#   }
# }
```

### Cost Analysis

```python
# Routing cost analysis
cost_analysis = agent.get_routing_cost_analysis()
# {
#   "total_cost_usd": 12.45,
#   "cost_per_request": 0.01245,
#   "savings_from_routing": 3.21,
#   "savings_percentage": 20.5,
#   "model_efficiency": {
#     "gpt-4o-mini": {"cost_per_quality": 0.0001},
#     "gpt-4o": {"cost_per_quality": 0.0003},
#     "claude-3-haiku": {"cost_per_quality": 0.00015}
#   }
# }
```

### Quality Metrics

```python
# Quality by model
quality_metrics = agent.get_quality_by_model()
# {
#   "gpt-4o-mini": {
#     "avg_quality_score": 0.85,
#     "success_rate": 0.95,
#     "user_satisfaction": 0.82
#   },
#   "gpt-4o": {
#     "avg_quality_score": 0.92,
#     "success_rate": 0.98,
#     "user_satisfaction": 0.91
#   },
#   "claude-3-haiku": {
#     "avg_quality_score": 0.88,
#     "success_rate": 0.96,
#     "user_satisfaction": 0.86
#   }
# }
```

---

## 🎛️ Custom Routing

### Custom Routing Functions

```python
def custom_routing_function(task_ir, context):
    # Business-specific routing logic
    if task_ir.metadata.get("department") == "legal":
        return {"provider": "anthropic", "model": "claude-3-opus"}
    elif task_ir.metadata.get("department") == "engineering":
        return {"provider": "openai", "model": "gpt-4o"}
    elif task_ir.metadata.get("priority") == "urgent":
        return {"provider": "anthropic", "model": "claude-3-haiku"}
    elif task_ir.privacy.get("level") == "high":
        return {"provider": "local", "model": "llama-2-7b"}
    else:
        return {"provider": "openai", "model": "gpt-4o-mini"}

agent = Agent(
    model="auto",
    routing_strategy=custom_routing_function
)
```

### Rule-Based Routing

```python
routing_rules = [
    {
        "condition": "intent == 'analyze' and complexity > 0.7",
        "action": {"provider": "openai", "model": "gpt-4o"},
        "priority": 1
    },
    {
        "condition": "intent == 'generate' and time_sensitive == True",
        "action": {"provider": "anthropic", "model": "claude-3-haiku"},
        "priority": 2
    },
    {
        "condition": "privacy.level == 'high'",
        "action": {"provider": "local", "model": "llama-2-7b"},
        "priority": 0  # Highest priority
    }
]

agent = Agent(
    model="auto",
    routing_rules=routing_rules
)
```

### ML-Based Routing

```python
# Train routing model
routing_model = train_routing_model(
    historical_data=usage_data,
    features=["intent", "complexity", "domain", "time_sensitive"],
    target="best_provider"
)

agent = Agent(
    model="auto",
    routing_strategy="ml_based",
    routing_model=routing_model
)
```

---

## 🚀 Advanced Routing Features

### Load Balancing

```python
agent = Agent(
    model="gpt-4o-mini",
    load_balancing="weighted_round_robin",
    provider_instances=[
        {"provider": "openai", "weight": 3, "api_key": "key1"},
        {"provider": "openai", "weight": 2, "api_key": "key2"},
        {"provider": "anthropic", "weight": 1, "api_key": "key3"}
    ]
)
```

### Geographic Routing

```python
def geographic_routing(task_ir, user_location):
    # Route to nearest data center
    if user_location.region == "europe":
        return {"provider": "anthropic", "model": "claude-3-haiku"}
    elif user_location.region == "asia":
        return {"provider": "openai", "model": "gpt-4o-mini"}
    else:
        return {"provider": "openai", "model": "gpt-4o"}

agent = Agent(
    model="auto",
    routing_strategy=geographic_routing,
    detect_location=True
)
```

### Time-Based Routing

```python
def time_based_routing(task_ir, current_time):
    # Route based on time and availability
    if current_time.hour < 6:  # Off-peak
        return {"provider": "openai", "model": "gpt-3.5-turbo"}
    elif current_time.hour < 18:  # Business hours
        return {"provider": "openai", "model": "gpt-4o-mini"}
    else:  # Peak hours
        return {"provider": "anthropic", "model": "claude-3-haiku"}

agent = Agent(
    model="auto",
    routing_strategy=time_based_routing
)
```

---

## 🔍 Routing Debugging

### Routing Trace

```python
result = agent.run("Analyze complex data", trace=True)

# Routing decision trace
print(result["routing_trace"])
# {
#   "task_analysis": {
#     "intent": "analyze",
#     "complexity": 0.8,
#     "domain": "data_analysis",
#     "time_sensitive": False
#   },
#   "routing_decision": {
#     "strategy": "balanced",
#     "selected_model": "gpt-4o",
#     "reasoning": "High complexity analysis task",
#     "alternatives_considered": ["gpt-4o-mini", "claude-3-sonnet"]
#   },
#   "fallback_info": {
#     "fallbacks_available": True,
#     "fallback_chain": ["claude-3-haiku", "gpt-3.5-turbo"],
#     "fallback_used": False
#   }
# }
```

### A/B Testing

```python
# Test routing strategies
ab_test = agent.test_routing_strategy(
    strategy_a="cost_optimized",
    strategy_b="balanced",
    test_duration_hours=24,
    success_metric="user_satisfaction"
)

# Results
# {
#   "strategy_a": {"satisfaction": 0.82, "cost": 0.08},
#   "strategy_b": {"satisfaction": 0.87, "cost": 0.12},
#   "winner": "strategy_b",
#   "confidence": 0.94
# }
```

---

## 🎯 Best Practices

### Production Routing

```python
agent = Agent(
    model="auto",
    routing_strategy="balanced",
    fallback_providers=[
        {"provider": "anthropic", "model": "claude-3-haiku"},
        {"provider": "openai", "model": "gpt-3.5-turbo"}
    ],
    routing_config={
        "enable_load_balancing": True,
        "enable_geographic_routing": True,
        "cache_routing_decisions": True,
        "monitor_routing_performance": True
    }
)
```

### Cost Control

```python
agent = Agent(
    model="auto",
    routing_strategy="cost_optimized",
    cost_limits={
        "per_request_limit": 0.01,
        "daily_limit": 10.0,
        "monthly_limit": 200.0
    },
    budget_alerts={
        "threshold": 0.8,
        "notification": "email"
    }
)
```

### Performance Monitoring

```python
agent = Agent(
    model="auto",
    routing_strategy="balanced",
    monitoring={
        "track_routing_decisions": True,
        "track_fallback_usage": True,
        "track_cost_efficiency": True,
        "track_quality_metrics": True,
        "alert_on_degradation": True
    }
)
```

---

## 🎯 Next Steps

Now that you understand routing:

1. **[Learn Debugging](debugging.md)** - Full pipeline tracing
2. **[Explore Examples](examples.md)** - Routing in action
3. **[Check API Reference](api-reference.md)** - Full routing API
4. **[See FAQ](faq.md)** - Common routing questions

---

*Ready to debug your LLM pipeline? Check out the [Debugging documentation](debugging.md)!*
