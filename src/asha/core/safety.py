# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Unified safety semantics across all ASHA execution paths."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class SafetyMode(Enum):
    """How ASHA responds when security processing fails."""

    STRICT = "strict"
    BALANCED = "balanced"
    OFF = "off"


def safety_mode_from_policy_mode(mode: str) -> SafetyMode:
    """
    Derive safety behavior from a policy mode string.

    ``lite`` uses minimal policy features but the same fail-open semantics as
    ``balanced`` (degraded fallback on total failure).
    """
    key = mode.lower()
    if key == "off":
        return SafetyMode.OFF
    if key == "strict":
        return SafetyMode.STRICT
    return SafetyMode.BALANCED


def resolve_safety_mode(
    mode: str,
    *,
    safety: Optional[SafetyMode] = None,
) -> SafetyMode:
    """Resolve effective safety mode from an explicit override or policy mode."""
    if safety is not None:
        return safety
    return safety_mode_from_policy_mode(mode)


def is_fail_closed(safety: SafetyMode) -> bool:
    return safety == SafetyMode.STRICT


def should_raise_on_failure(safety: SafetyMode) -> bool:
    return safety == SafetyMode.STRICT


def security_enabled(safety: SafetyMode) -> bool:
    return safety != SafetyMode.OFF
