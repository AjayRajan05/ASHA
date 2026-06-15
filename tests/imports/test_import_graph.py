# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Import graph smoke tests for canonical module paths."""

from __future__ import annotations

import importlib


def test_core_engines_importable() -> None:
    mod = importlib.import_module("privysha.core.engines")
    assert callable(mod.sanitize_text)
    assert callable(mod.compile_prompt)
    assert callable(mod.optimize_tokens)


def test_runtime_prompt_processor_importable() -> None:
    mod = importlib.import_module("privysha.runtime")
    assert hasattr(mod, "PromptProcessor")
    assert hasattr(mod, "ExecutionProfile")
    assert not hasattr(mod, "Processor")


def test_integrations_wrap_llm_importable() -> None:
    mod = importlib.import_module("privysha.integrations")
    assert callable(mod.wrap_llm)
    assert callable(mod.auto_patch)


def test_compat_legacy_results_importable() -> None:
    mod = importlib.import_module("privysha.compat.legacy_results")
    assert callable(mod.to_legacy_pipeline_dict)


def test_types_results_importable() -> None:
    mod = importlib.import_module("privysha.types")
    assert hasattr(mod, "ProcessResult")
