"""Comprehensive smoke tests for PrivySHA package readiness."""

from pathlib import Path

import pytest

from privysha import Agent, process, ThreatType, HybridPIIDetector
from privysha.pipeline import Pipeline
from privysha.adapters.factory import AdapterFactory


REQUIRED_FILES = [
    "src/privysha/__init__.py",
    "src/privysha/agent.py",
    "src/privysha/pipeline/pipeline.py",
    "src/privysha/pipeline/stages/security_stage.py",
    "src/privysha/parser/__init__.py",
    "src/privysha/parser/prompt_ast.py",
    "src/privysha/adapters/factory.py",
    "src/privysha/adapters/mock_adapter.py",
    "src/privysha/adapters/base.py",
    "src/privysha/utils/dropin.py",
    "src/privysha/utils/pii_detector.py",
    "README.md",
    "LICENSE",
    "pyproject.toml",
]


def test_package_structure():
    """Verify the modular package layout exists."""
    missing = [f for f in REQUIRED_FILES if not Path(f).exists()]
    assert not missing, f"Missing files: {missing}"


def test_public_api_imports():
    """Core public API and lazy imports resolve."""
    assert Agent is not None
    assert process is not None
    assert ThreatType is not None
    assert HybridPIIDetector is not None


def test_dropin_process():
    """Drop-in process() masks PII and returns a string."""
    result = process("Contact john@example.com for help")
    assert isinstance(result, str)
    assert "john@example.com" not in result


def test_agent_pipeline_trace():
    """Agent runs the full pipeline with mock adapter."""
    agent = Agent(model="mock", privacy=True, token_budget=1200)
    test_prompt = (
        "Hey bro can you analyze this dataset for anomalies? "
        "Contact me at john@example.com"
    )
    result = agent.run(test_prompt, trace=True)

    for stage in ("prompts", "response"):
        assert stage in result, f"Missing key: {stage}"

    sanitized = result["prompts"]["sanitized"]
    assert "john@example.com" not in sanitized


def test_adapters():
    """Adapter factory creates mock and ollama adapters."""
    mock_adapter = AdapterFactory.create("mock")
    response = mock_adapter.generate("test prompt")
    assert isinstance(response, str)

    ollama_adapter = AdapterFactory.create("llama3")
    assert ollama_adapter is not None


def test_modular_pipeline_stages():
    """Individual pipeline stages initialize and the pipeline processes text."""
    from privysha.pipeline.stages import (
        SecurityStage,
        IRGenerationStage,
        OptimizationStage,
    )

    SecurityStage()
    IRGenerationStage()
    OptimizationStage()

    pipeline = Pipeline(privacy=True, token_budget=1200)
    result = pipeline.process("analyze dataset for anomalies")
    assert "prompts" in result
    assert "sanitized" in result["prompts"]
    assert "compiled" in result["prompts"]


def test_documentation():
    """README contains required sections."""
    readme = Path("README.md").read_text(encoding="utf-8", errors="ignore")
    assert len(readme) >= 1000
    for section in ("# Overview", "# Installation", "# Quick Start", "# Key Features"):
        assert section in readme, f"Missing README section: {section}"

