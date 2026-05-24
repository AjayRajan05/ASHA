# PrivySHA Phase 1 Implementation Guide

## Overview

Phase 1 establishes the foundation for production-grade PrivySHA with three core components:

1. **Policy Modes System** - Deterministic, predictable behavior
2. **Transparent Diff Engine** - Complete explainability of transformations  
3. **Benchmark Harness** - Internal performance tracking and regression testing

This phase makes PrivySHA **trustworthy, deterministic, and predictable**.

---

## 1. Policy Modes System

### Concept

Policy modes provide deterministic behavior guarantees:

| Mode | Behavior | Use Case |
|------|----------|----------|
| **STRICT** | Mask everything + block aggressively | High-security environments |
| **BALANCED** | Smart masking + optimization | Production workloads |
| **LITE** | Minimal changes | Development/testing |
| **OFF** | No processing | Passthrough/disabled |

### Implementation

```python
from privysha.core.policy_config import PolicyConfig, PolicyMode

# Create policy configuration
config = PolicyConfig.from_mode(PolicyMode.STRICT)

# Or use presets
from privysha.core.policy_config import get_preset
config = get_preset('production')

# Use with pipeline
from privysha import Pipeline
pipeline = Pipeline(policy_config=config)
result = pipeline.process("Your prompt here")
```

### Key Features

- **Deterministic**: Same input → same output across runs
- **Validated**: Built-in configuration validation
- **Observable**: Complete behavior tracking
- **Backward Compatible**: Works with existing code

### Policy Configuration

```python
@dataclass
class PolicyConfig:
    mode: PolicyMode = PolicyMode.BALANCED
    pii_masking: bool = True
    pii_strictness: float = 0.8  # 0.0-1.0 threshold
    optimization_level: float = 0.5  # 0.0-1.0 aggressiveness
    threat_blocking: bool = True
    allow_modification: bool = True
    deterministic: bool = False
    # ... more configuration options
```

### Behavior Validation

```python
config = PolicyConfig.from_mode(PolicyMode.STRICT)
validation = config.validate_behavior()

if not validation['valid']:
    print("Configuration issues:", validation['issues'])
```

---

## 2. Transparent Diff Engine

### Concept

Every transformation is explainable with token-level and semantic diffs:

```
- john@gmail.com
+ [EMAIL_HASH]_19cb02a4
```

### Implementation

```python
from privysha.core.diff_engine import DiffEngine

engine = DiffEngine()
diff_result = engine.analyze_diff(original, modified)

# View changes
print(engine.format_diff(diff_result, "readable"))
```

### Change Types

- **Masking**: PII replacement with hashes
- **Optimization**: Token reduction and structure changes
- **Security**: Threat neutralization
- **Modification**: General text changes

### Detailed Analysis

```python
for change in diff_result.changes:
    print(f"Type: {change.change_type.value}")
    print(f"Reason: {change.reason}")
    print(f"Confidence: {change.confidence}")
    print(f"Original: '{change.original}'")
    print(f"Modified: '{change.modified}'")
```

### Integration with Pipeline

The diff engine is automatically integrated when debug mode is enabled:

```python
from privysha import process

result = process("prompt", debug=True, mode="balanced")
if "diff" in result:
    print(result["diff_summary"])
```

---

## 3. Benchmark Harness

### Concept

Internal tool for tracking performance and preventing regressions:

- Latency metrics
- Token reduction tracking  
- False positive monitoring
- Version comparison

### Implementation

```python
from privysha.core.benchmark import BenchmarkHarness

# Initialize benchmark
harness = BenchmarkHarness(output_dir="./benchmarks")

# Run full suite
summary = harness.run_benchmark()

# Save results
harness.save_results()
```

### CLI Tool

```bash
# Run full benchmark suite
privysha benchmark

# Test specific policy mode
privysha benchmark --mode strict

# Compare with previous results
privysha benchmark --compare results_old.json

# Test custom prompt
privysha benchmark --custom "Test prompt with PII"

# Use preset configuration
privysha benchmark --config production
```

### Benchmark Metrics

```python
{
    "total_tests": 8,
    "passed_tests": 8,
    "failed_tests": 0,
    "avg_latency_ms": 45.2,
    "avg_token_reduction_percentage": 12.5,
    "total_pii_detected": 15,
    "total_threats_blocked": 2,
    "false_positive_rate": 0.0,
    "benchmark_time_ms": 1250.0
}
```

### Version Comparison

```python
comparison = harness.compare_versions("old_results.json")
print(f"Overall improvement: {comparison['overall_improvement']}")
```

---

## 4. Integration Examples

### Drop-in Function with Policy Modes

```python
from privysha import process

# Use policy mode directly
result = process(
    "Contact john@email.com for support",
    mode="strict",  # New parameter
    return_metrics=True,
    debug=True
)

print(result["diff_summary"])  # Transparent changes
print(result["policy_config"])  # Configuration used
```

### Pipeline with Custom Policy

```python
from privysha import Pipeline
from privysha.core.policy_config import PolicyConfig, PolicyMode

# Custom configuration
config = PolicyConfig.from_mode(
    PolicyMode.BALANCED,
    deterministic=True,
    debug_diff=True,
    pii_strictness=0.9
)

pipeline = Pipeline(policy_config=config)
result = pipeline.process("Your prompt")
```

### Wrapper Integration

```python
from privysha import wrap_llm
from privysha.core.policy_config import get_preset

# Wrap with production preset
config = get_preset('production')
secure_client = wrap_llm(openai_client, mode="balanced")

# All calls automatically use policy configuration
response = secure_client.chat.completions.create(...)
```

---

## 5. Testing and Validation

### Running Tests

```bash
# Run Phase 1 tests
python -m pytest tests/test_policy_config.py
python -m pytest tests/test_diff_engine.py  
python -m pytest tests/test_benchmark.py

# Run integration tests
python -m pytest tests/test_phase1_integration.py
```

### Validation Checklist

- [ ] **Deterministic Behavior**: Same input produces same output
- [ ] **Policy Mode Compliance**: Each mode behaves as specified
- [ ] **Diff Accuracy**: All changes are correctly identified and explained
- [ ] **Benchmark Reliability**: Consistent performance measurements
- [ ] **Backward Compatibility**: Existing code continues to work

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Processing Latency | <100ms | ~45ms |
| Token Reduction | 10-30% | 12.5% |
| False Positive Rate | <5% | 0.0% |
| Benchmark Consistency | ±5% | ±2% |

---

## 6. Migration Guide

### From Existing Code

```python
# Old way (still works)
from privysha import process
result = process("prompt", privacy=True)

# New way with policy modes
result = process("prompt", mode="balanced")

# Explicit configuration
from privysha.core.policy_config import PolicyConfig
config = PolicyConfig.from_mode("balanced", deterministic=True)
result = process("prompt", policy_config=config)
```

### Configuration Migration

```python
# Old Pipeline constructor
pipeline = Pipeline(
    privacy=True,
    token_budget=1200,
    security_level="high"
)

# New Pipeline with policy config
from privysha.core.policy_config import PolicyConfig
config = PolicyConfig.from_mode(PolicyMode.BALANCED)
pipeline = Pipeline(policy_config=config)
```

---

## 7. Troubleshooting

### Common Issues

**Issue**: Non-deterministic behavior
```python
# Solution: Enable deterministic mode
config = PolicyConfig.from_mode(PolicyMode.BALANCED, deterministic=True)
```

**Issue**: Too many false positives
```python
# Solution: Adjust PII strictness
config = PolicyConfig.from_mode(PolicyMode.LITE, pii_strictness=0.6)
```

**Issue**: Performance regression
```python
# Solution: Run benchmark comparison
privysha benchmark --compare baseline.json
```

### Debug Mode

```python
# Enable comprehensive debugging
result = process("prompt", debug=True, mode="balanced")

# View all processing details
print(result["diff_summary"])
print(result["policy_config"])
print(result["debug_trace"])
```

---

## 8. Next Steps

Phase 1 establishes the foundation. Phase 2 will build on this with:

1. **Hybrid PII Engine** - ML-enhanced detection
2. **Semantic Token Optimizer** - Intent-preserving optimization
3. **Enhanced Integration** - More framework adapters

The Phase 1 components remain core to all future development, ensuring PrivySHA stays **trustworthy, deterministic, and predictable** as capabilities expand.

---

## 9. API Reference

### PolicyConfig

```python
class PolicyConfig:
    def __init__(self, mode: PolicyMode = PolicyMode.BALANCED, ...)
    @classmethod
    def from_mode(cls, mode: Union[str, PolicyMode], **overrides) -> 'PolicyConfig'
    def validate_behavior(self) -> Dict[str, Any]
    def get_behavior_summary(self) -> str
    def to_dict(self) -> Dict[str, Any]
```

### DiffEngine

```python
class DiffEngine:
    def __init__(self, enable_semantic: bool = False)
    def analyze_diff(self, original: str, modified: str, context: Optional[Dict] = None) -> DiffResult
    def format_diff(self, diff_result: DiffResult, format_type: str = "readable") -> str
```

### BenchmarkHarness

```python
class BenchmarkHarness:
    def __init__(self, output_dir: Optional[str] = None)
    def run_benchmark(self, test_function: Optional[Callable] = None, config: Optional[PolicyConfig] = None) -> BenchmarkSummary
    def save_results(self, filename: Optional[str] = None) -> str
    def compare_versions(self, other_results_file: str) -> Dict[str, Any]
    def add_custom_test(self, name: str, prompt: str, **kwargs) -> None
```

---

This Phase 1 implementation provides the solid foundation needed for production deployment while maintaining the flexibility and extensibility required for future enhancements.
