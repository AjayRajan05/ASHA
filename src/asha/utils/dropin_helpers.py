# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Shared helpers for drop-in API modules."""

from __future__ import annotations

import warnings
from typing import Any, Union

from ..core.security.security_layer import SecurityLevel
from ..types.results import OptimizeResult, ProcessResult, SanitizeResult


def normalize_security_level(level: Union[str, SecurityLevel]) -> str:
    if isinstance(level, SecurityLevel):
        return level.name
    return str(level).upper()


def coerce_process_output(processed: Any, fallback: str) -> str:
    """Normalize process() return value to a prompt string."""
    if isinstance(processed, ProcessResult):
        return processed.output
    if isinstance(processed, OptimizeResult):
        return processed.output
    if isinstance(processed, SanitizeResult):
        return processed.output
    if isinstance(processed, str):
        return processed
    if isinstance(processed, dict):
        if processed.get("optimized"):
            return str(processed["optimized"])
        if processed.get("output"):
            return str(processed["output"])
        prompts = processed.get("prompts", {})
        if isinstance(prompts, dict) and prompts.get("optimized"):
            return str(prompts["optimized"])
    return fallback


def warn_deprecated(name: str, replacement: str) -> None:
    warnings.warn(
        f"{name} is deprecated; {replacement}",
        DeprecationWarning,
        stacklevel=3,
    )
