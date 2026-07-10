# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Unified mode and stage-flag resolution for predictable API behavior."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .policy_config import PolicyConfig, PolicyMode
from .safety import SafetyMode


def resolve_effective_privacy(mode: str, privacy: bool) -> bool:
    """
    Resolve privacy flag against mode.

    Precedence:
    - mode="off" -> privacy disabled regardless of privacy= argument
    - otherwise privacy= argument wins (default True for balanced/strict/lite)
    """
    if mode.lower() == "off":
        return False
    return privacy


def policy_from_mode(mode: str) -> PolicyConfig:
    """Build PolicyConfig from mode string."""
    key = mode.lower()
    if key == "off":
        return PolicyConfig.from_mode(PolicyMode.OFF)
    if key == "strict":
        return PolicyConfig.from_mode(PolicyMode.STRICT)
    if key == "lite":
        return PolicyConfig.from_mode(PolicyMode.LITE)
    return PolicyConfig.from_mode(PolicyMode.BALANCED)


def apply_stage_flags(
    policy: PolicyConfig,
    *,
    security: bool,
    compile: bool,
    optimize: bool,
    privacy: bool,
) -> PolicyConfig:
    """
    Apply explicit stage toggles from process() onto a PolicyConfig.

    security=False -> disable PII and injection detection
    compile=False  -> allow_modification=False (skip IR/compile transforms)
    optimize=False -> enable_optimization=False
    """
    if not security or not privacy:
        policy.pii_masking = False
        policy.enable_pii_detection = False
        policy.enable_injection_detection = False
        policy.threat_blocking = False

    if not compile:
        policy.allow_modification = False

    if not optimize:
        policy.enable_optimization = False

    return policy


def build_pipeline_config(
    *,
    mode: str,
    privacy: bool,
    security: bool,
    compile: bool,
    optimize: bool,
    safety_mode: SafetyMode,
    pii_mode: str = "rule",
    reversible: bool = False,
    preserve_intent: bool = False,
    security_level: str = "medium",
    debug: bool = False,
    extra: Optional[Dict[str, Any]] = None,
) -> Tuple[PolicyConfig, bool, Dict[str, Any]]:
    """
    Build final pipeline policy dict and effective privacy flag.

    Returns (policy_config, effective_privacy, policy_dict).
    """
    effective_privacy = resolve_effective_privacy(mode, privacy)
    policy = policy_from_mode(mode)
    policy = apply_stage_flags(
        policy,
        security=security,
        compile=compile,
        optimize=optimize,
        privacy=effective_privacy,
    )
    if debug:
        policy.debug_diff = True

    policy_dict = policy.to_dict()
    policy_dict["safety_mode"] = safety_mode.value
    policy_dict["pii_mode"] = pii_mode
    policy_dict["reversible"] = reversible
    policy_dict["preserve_intent"] = preserve_intent
    policy_dict["security_level"] = security_level
    # Slim pipeline: routing/generation removed from default path (v0.4)
    if extra:
        policy_dict.update(extra)
    return policy, effective_privacy, policy_dict
