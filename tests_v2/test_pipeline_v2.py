import pytest
from privysha.pipeline.pipeline import Pipeline


def test_modular_pipeline_full_flow():
    """Test the modular pipeline (Optimization + Security)."""
    pipeline = Pipeline(
        token_budget=1000,
        security_level="MEDIUM",
        debug_enabled=True,
    )
    
    input_text = "Summarize this: John Doe (john@example.com) is a great developer with 10 years of experience."
    
    result = pipeline.process(input_text)
    
    assert result["success"] is True
    assert "prompts" in result
    assert "optimized" in result["prompts"]
    assert "original" in result["prompts"]
    
    # Check security result (PII masking) — compiled dict from result stage
    assert "security_result" in result
    security = result["security_result"]
    is_safe = security.get("is_safe", True) if isinstance(security, dict) else security.is_safe
    assert is_safe is True
    
    # Optimized text should be shorter or more efficient
    optimized = result["prompts"]["optimized"]
    assert len(optimized) > 0
    sanitized = result["prompts"]["sanitized"]
    assert "john@example.com" not in sanitized
    assert "john@example.com" not in optimized

def test_modular_pipeline_token_optimization():
    """Test token budget enforcement."""
    pipeline = Pipeline(token_budget=10) # Very tight budget
    
    long_text = "This is a very long text that should be significantly optimized to fit into a very small token budget of just ten tokens."
    
    result = pipeline.process(long_text)
    
    assert result["success"] is True
    optimized = result["prompts"]["optimized"]
    
    # Check if optimization metrics are present
    assert "optimization_metrics" in result
    metrics = result["optimization_metrics"]
    assert "token_reduction_percentage" in metrics

def test_modular_pipeline_routing():
    """Test model routing decision."""
    pipeline = Pipeline()
    
    input_text = "Simple greeting"
    result = pipeline.process(input_text)
    
    assert "routing_decision" in result
    # For simple input, it might choose a "lite" model
    
def test_modular_pipeline_trace():
    """Test execution tracing."""
    pipeline = Pipeline()
    
    result = pipeline.process("Hello world", trace=True)
    
    assert "trace" in result
    trace = result["trace"]
    assert "stages" in trace
    assert len(trace["stages"]) > 0

if __name__ == "__main__":
    pytest.main([__file__])
