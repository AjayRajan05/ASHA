# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Core compiler primitives (internal — use process/sanitize at top level)."""

from .policy_resolution import (
    apply_stage_flags,
    build_pipeline_config,
    policy_from_mode,
    resolve_effective_privacy,
)

__all__ = [
    "apply_stage_flags",
    "build_pipeline_config",
    "policy_from_mode",
    "resolve_effective_privacy",
    "sanitize_text",
    "compile_prompt",
    "optimize_tokens",
]


from typing import Any


def __getattr__(name: str) -> Any:
    if name in ("sanitize_text", "compile_prompt", "optimize_tokens"):
        from . import engines as _engines
        return getattr(_engines, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
