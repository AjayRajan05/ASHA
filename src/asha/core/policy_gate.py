# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Policy gate helpers for deterministic processing passthrough behavior."""

from typing import Any, Dict


def should_passthrough(config: Dict[str, Any]) -> bool:
    """Return True when all processing should be skipped."""
    mode = config.get("mode", "")
    if isinstance(mode, str) and mode.lower() == "off":
        return True

    enable_pii = config.get("enable_pii_detection", True)
    enable_injection = config.get("enable_injection_detection", True)
    enable_optimization = config.get("enable_optimization", True)

    if not enable_pii and not enable_injection and not enable_optimization:
        return True

    return False


def security_disabled(config: Dict[str, Any]) -> bool:
    """Return True when security processing should be skipped."""
    enable_pii = config.get("enable_pii_detection", True)
    enable_injection = config.get("enable_injection_detection", True)
    pii_masking = config.get("pii_masking", config.get("privacy", True))
    if not pii_masking:
        enable_pii = False
    return not enable_pii and not enable_injection


def optimization_disabled(config: Dict[str, Any]) -> bool:
    """Return True when optimization should be skipped."""
    return not config.get("enable_optimization", True)


def modification_disabled(config: Dict[str, Any]) -> bool:
    """Return True when IR/compilation should not transform content."""
    return config.get("allow_modification") is False


def create_passthrough_result(content: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Build a legacy result dict with unchanged content."""
    return {
        "success": True,
        "passthrough": True,
        "policy_mode": config.get("mode", "off"),
        "prompts": {
            "original": content,
            "sanitized": content,
            "compiled": content,
            "optimized": content,
        },
        "security_result": {
            "is_safe": True,
            "detected_threats": [],
            "masked_entities": {},
            "sanitized_content": content,
            "threat_level": "LOW",
            "security_score": 0.0,
            "recommendations": [],
            "processing_time_ms": 0.0,
            "skipped": True,
        },
        "routing_decision": default_routing_decision(),
        "optimization_metrics": {"token_reduction_percentage": 0},
        "performance_metrics": {"total_pipeline_ms": 0},
        "stage_metrics": {},
    }


def default_routing_decision() -> Dict[str, Any]:
    """Placeholder routing metadata for legacy dict consumers."""
    return {
        "selected_model": "default",
        "provider": "unknown",
        "confidence": 0.5,
        "reasoning": "fallback_routing",
        "estimated_cost": 0.0,
    }
