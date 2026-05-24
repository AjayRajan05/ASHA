# ⚡ PrivySHA Performance Tuning Guide

**Optimize PrivySHA for maximum speed and efficiency**

---

## 🎯 Performance Overview

PrivySHA is designed for **sub-100ms processing** with **minimal memory overhead**. This guide helps you achieve optimal performance for your specific use case.

---

## 📊 Baseline Performance

| Operation | Typical Time | Memory Usage |
|------------|----------------|---------------|
| Basic processing | 20-40ms | <50MB |
| With PII detection | 25-60ms | <75MB |
| Full pipeline | 40-80ms | <100MB |
| With observability | 50-120ms | <120MB |

---

## 🚀 Speed Optimization

### **1. Choose the Right Mode**

```python
# Fastest: Minimal processing
result = process(
    prompt,
    mode="lite",           # Minimal overhead
    security_level="low",    # Basic security only
    pii_mode="rule",        # Fastest PII detection
    debug=False,             # No debug overhead
    trace=False              # No tracing overhead
)

# Balanced: Good performance + features
result = process(
    prompt,
    mode="balanced",         # Default balance
    security_level="medium",  # Standard security
    pii_mode="hybrid"        # Good accuracy/speed
)

# Maximum features: Slower but comprehensive
result = process(
    prompt,
    mode="strict",           # Maximum optimization
    security_level="high",    # Full security
    pii_mode="ml_only",       # Best accuracy
    debug=True,             # Full debugging
    trace=True              # Complete tracing
)
```

### **2. Optimize Token Budget**

```python
# For speed: Small token budget
result = process(prompt, token_budget=500)

# For cost savings: Aggressive optimization  
result = process(prompt, token_budget=200)

# For quality: Larger budget
result = process(prompt, token_budget=2000)
```

### **3. Use Async Processing**

```python
import asyncio
from privysha import process_async

# Batch processing for high throughput
async def process_batch(prompts):
    tasks = [process_async(p) for p in prompts]
    results = await asyncio.gather(*tasks)
    return results

# Single async call
result = await process_async(prompt)
```

### **4. Disable Unused Features**

```python
# Disable observability overhead
result = process(
    prompt,
    trace=False,      # No tracing (~10-20ms faster)
    debug=False,      # No debug output (~5-10ms faster)
    log_level="INFO"  # Minimal logging
)

# Disable expensive security
result = process(
    prompt,
    security_level="low",    # Skip advanced checks (~15-25ms faster)
    pii_mode="rule"         # Use rule-based only (~10-15ms faster)
)
```

---

## 💾 Memory Optimization

### **1. Minimize Context**

```python
# Use smaller context for less memory
result = process(
    prompt,
    context_config={
        "role": "analyst",           # Specific vs general
        "specialization": "data"      # Focused scope
    }
)
```

### **2. Process in Batches**

```python
from privysha import Agent

# Reuse agent for multiple prompts
agent = Agent(model="gpt-4o-mini", privacy=True)

# Process multiple prompts efficiently
results = []
for prompt in large_prompt_list:
    result = agent.run(prompt)
    results.append(result)
    # Agent maintains internal state
```

### **3. Clear Caches**

```python
from privysha import Agent

# Periodically clear agent state
agent = Agent(model="gpt-4o-mini")

# After processing many prompts
if hasattr(agent, 'clear_cache'):
    agent.clear_cache()

# Or create fresh agent
agent = Agent(model="gpt-4o-mini")  # Fresh instance
```

---

## 🔧 Configuration Tuning

### **High-Throughput Applications**

```python
# For APIs, chatbots, real-time processing
config = {
    "mode": "lite",
    "security_level": "low", 
    "pii_mode": "rule",
    "token_budget": 800,
    "debug": False,
    "trace": False
}

agent = Agent(**config)
```

### **Batch Processing Applications**

```python
# For data processing, analysis pipelines
config = {
    "mode": "balanced",
    "security_level": "medium",
    "pii_mode": "hybrid",
    "token_budget": 1500,
    "debug": False,
    "trace": False
}

agent = Agent(**config)
```

### **Development & Debugging**

```python
# During development only
config = {
    "mode": "strict",
    "security_level": "high",
    "pii_mode": "ml_only",
    "debug": True,
    "trace": True,
    "log_level": "DEBUG"
}

agent = Agent(**config)
```

---

## 📈 Performance Monitoring

### **1. Benchmark Your Setup**

```python
import time
from privysha import process

def benchmark(prompt, iterations=100):
    times = []
    
    for _ in range(iterations):
        start = time.time()
        result = process(prompt)
        end = time.time()
        times.append((end - start) * 1000)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Average: {avg_time:.2f}ms")
    print(f"Min: {min_time:.2f}ms") 
    print(f"Max: {max_time:.2f}ms")
    print(f"P95: {sorted(times)[94]:.2f}ms")
    
    return {
        "average_ms": avg_time,
        "min_ms": min_time,
        "max_ms": max_time,
        "p95_ms": sorted(times)[94]
    }

# Usage
benchmark("Analyze customer data with john@example.com")
```

### **2. Monitor Memory Usage**

```python
import psutil
import os
from privysha import process

def monitor_memory():
    process = psutil.Process(os.getpid())
    
    # Before processing
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Process
    result = process("Large prompt with PII data...")
    
    # After processing  
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = memory_after - memory_before
    
    print(f"Memory used: {memory_used:.2f}MB")
    print(f"Peak memory: {memory_after:.2f}MB")
    
    return {
        "memory_used_mb": memory_used,
        "peak_memory_mb": memory_after
    }

monitor_memory()
```

### **3. Track Performance Metrics**

```python
from privysha import process

def detailed_metrics(prompt):
    result = process(
        prompt,
        trace=True,
        return_metrics=True
    )
    
    # Access detailed performance data
    metrics = result["metrics"]
    trace = result["trace"]
    
    print("=== PERFORMANCE METRICS ===")
    print(f"Total latency: {metrics.total_latency_ms}ms")
    print(f"Stages run: {metrics.stages_run}")
    print(f"Tokens saved: {metrics.tokens_saved}")
    print(f"PII detected: {metrics.pii_detected}")
    print(f"Changes made: {metrics.changes_made}")
    
    print("\n=== STAGE BREAKDOWN ===")
    for stage in trace["stages"]:
        print(f"{stage['name']}: {stage['latency_ms']}ms")
    
    return result

detailed_metrics("Process customer inquiry with contact info")
```

---

## 🎛️ Specific Use Cases

### **Chatbots & Real-time**

```python
# Optimize for response time <50ms
config = {
    "mode": "lite",
    "security_level": "low",
    "pii_mode": "rule",
    "token_budget": 600,
    "debug": False
}

agent = Agent(**config)
response = agent.run(user_message)  # ~30-50ms
```

### **Data Processing Pipelines**

```python
# Optimize for accuracy and cost savings
config = {
    "mode": "balanced",
    "security_level": "medium", 
    "pii_mode": "hybrid",
    "token_budget": 1500,
    "debug": False
}

agent = Agent(**config)
results = [agent.run(batch) for batch in data_batches]
```

### **Content Moderation**

```python
# Optimize for security and compliance
config = {
    "mode": "strict",
    "security_level": "high",
    "pii_mode": "ml_only",
    "token_budget": 1000,
    "debug": True  # For audit trail
}

agent = Agent(**config)
moderation_result = agent.run(content_to_moderate)
```

### **Development & Testing**

```python
# Optimize for debugging and iteration
config = {
    "mode": "strict",
    "security_level": "high",
    "pii_mode": "ml_only", 
    "debug": True,
    "trace": True,
    "log_level": "DEBUG"
}

agent = Agent(**config)
result = agent.run(test_prompt)
```

---

## 🚨 Common Performance Issues

### **Issue: Processing >200ms**

**Symptoms:**
- Slow response times
- High memory usage
- Timeouts

**Solutions:**
```python
# 1. Use lite mode
result = process(prompt, mode="lite")

# 2. Reduce token budget
result = process(prompt, token_budget=500)

# 3. Disable ML features
result = process(prompt, pii_mode="rule")

# 4. Use async processing
result = await process_async(prompt)
```

### **Issue: Memory Leaks**

**Symptoms:**
- Memory usage increases over time
- System slows down
- Crashes after many requests

**Solutions:**
```python
# 1. Use fresh agent instances
def process_with_fresh_agent(prompt):
    agent = Agent(model="gpt-4o-mini")
    return agent.run(prompt)

# 2. Clear caches periodically
if request_count % 1000 == 0:
    agent = Agent(model="gpt-4o-mini")  # Fresh instance

# 3. Monitor memory usage
import psutil
process = psutil.Process()
if process.memory_info().rss > 500 * 1024 * 1024:  # 500MB
    print("Warning: High memory usage detected")
```

### **Issue: High CPU Usage**

**Symptoms:**
- High CPU utilization
- System slowdown
- Fan running constantly

**Solutions:**
```python
# 1. Reduce security level
result = process(prompt, security_level="low")

# 2. Use rule-based PII detection
result = process(prompt, pii_mode="rule")

# 3. Process in batches vs continuous
def batch_process(prompts, batch_size=10):
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i+batch_size]
        results = [process(p) for p in batch]
        # Brief pause between batches
        time.sleep(0.1)
```

---

## 📊 Performance Targets

| Application Type | Target Latency | Acceptable Range |
|-----------------|----------------|-----------------|
| Real-time Chat | <50ms | 30-80ms |
| API Backend | <100ms | 50-200ms |
| Batch Processing | <200ms | 100-500ms |
| Data Analysis | <150ms | 80-300ms |
| Content Moderation | <300ms | 200-800ms |

---

## 🔍 Profiling Tools

### **Python Profiler**
```python
import cProfile
import pstats
from privysha import process

def profile_processing():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run processing
    result = process("Your test prompt here")
    
    profiler.disable()
    
    # Save stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    return result

profile_processing()
```

### **Line Profiler**
```python
import line_profiler
from privysha import process

@line_profiler.profile
def profile_line_by_line():
    return process("Test prompt for profiling")

profile_line_by_line()
```

---

## 🎯 Best Practices

### **1. Right Tool for the Job**
- **Real-time**: Use `process()` with lite mode
- **Batch processing**: Use `process_async()` 
- **Development**: Use Agent with full debugging
- **Production**: Use balanced mode with monitoring

### **2. Configuration Management**
```python
# Environment-based configuration
import os

config = {
    "mode": os.getenv("PRIVYSHA_MODE", "balanced"),
    "security_level": os.getenv("PRIVYSHA_SECURITY", "medium"),
    "pii_mode": os.getenv("PRIVYSHA_PII_MODE", "hybrid"),
    "token_budget": int(os.getenv("PRIVYSHA_TOKEN_BUDGET", "1200"))
}
```

### **3. Error Handling**
```python
from privysha import process

def robust_processing(prompt):
    try:
        result = process(prompt, mode="lite")
        return result
    except Exception as e:
        # Fallback to minimal processing
        return process(prompt, mode="off")
```

### **4. Resource Management**
```python
# Connection pooling for high-throughput
from privysha import Agent

class AgentPool:
    def __init__(self, pool_size=5):
        self.agents = [Agent(mode="lite") for _ in range(pool_size)]
        self.current = 0
    
    def get_agent(self):
        agent = self.agents[self.current]
        self.current = (self.current + 1) % len(self.agents)
        return agent

pool = AgentPool(pool_size=3)
agent = pool.get_agent()
result = agent.run(prompt)
```

---

## 📈 Monitoring in Production

### **Key Metrics to Track**
- **Latency**: Average, P95, P99
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Memory Usage**: Peak and average
- **Token Efficiency**: Tokens saved percentage

### **Alerting Thresholds**
```python
# Set up alerts for performance issues
ALERT_THRESHOLDS = {
    "latency_p95_ms": 200,      # Alert if P95 > 200ms
    "error_rate_percent": 5,       # Alert if error rate > 5%
    "memory_peak_mb": 500,          # Alert if memory > 500MB
    "throughput_rps": 100,          # Alert if throughput < 100 RPS
}
```

---

## 🎉 Conclusion

**PrivySHA Performance Hierarchy:**

1. **Lite Mode** → Fastest (~20-40ms)
2. **Rule-based PII** → Faster (~10-15ms improvement)  
3. **Async Processing** → Highest throughput
4. **Proper Configuration** → Optimal balance
5. **Monitoring** → Sustained performance

**With proper tuning, PrivySHA can achieve:**
- ✅ **Sub-50ms processing** for real-time use cases
- ✅ **High throughput** for batch processing
- ✅ **Low memory footprint** for resource-constrained environments
- ✅ **Consistent performance** through proper monitoring

**Start with the recommended configuration for your use case, then tune based on your actual performance metrics!**
