"""Backward compatibility for public API exports."""

import privysha


def test_core_exports_present():
    expected = [
        "process",
        "sanitize",
        "optimize",
        "wrap_llm",
        "auto_patch",
        "Agent",
        "Pipeline",
        "PolicyConfig",
    ]
    for name in expected:
        assert hasattr(privysha, name), f"Missing export: {name}"


def test_process_callable():
    assert callable(privysha.process)
