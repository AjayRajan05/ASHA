# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Internal execution context for PromptProcessor (not public API)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..core.safety import SafetyMode
from .profiles import ExecutionProfile


@dataclass(frozen=True)
class RunContext:
    """Resolved knobs for a single processor invocation."""

    mode: str
    profile: ExecutionProfile
    safety: SafetyMode
    effective_privacy: bool
    security: bool
    compile: bool
    optimize: bool
    token_budget: int = 1200
    pii_mode: str = "rule"
    reversible: bool = False
    preserve_intent: bool = False
    security_level: str = "medium"
    trace: bool = False
    debug: bool = False
    log_level: str = "INFO"
    log_output: str = "console"
    log_file: Optional[str] = None
    include_legacy_detail: bool = False
