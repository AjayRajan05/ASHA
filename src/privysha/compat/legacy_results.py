# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Legacy dict-shaped results for deprecated Pipeline consumers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.policy_gate import default_routing_decision
from ..types.results import ProcessResult
from .warnings import warn_legacy_dict


def process_result_to_legacy_dict(result: ProcessResult) -> Dict[str, Any]:
    """Convert a ProcessResult to the old Pipeline.process() dict shape."""
    warn_legacy_dict()
    if result.legacy_detail:
        legacy = dict(result.legacy_detail)
        legacy.setdefault("routing_decision", default_routing_decision())
        legacy["success"] = legacy.get("success", not result.degraded)
        if result.trace:
            legacy["trace"] = result.trace
        if result.diff:
            legacy["diff"] = result.diff
        return legacy

    return {
        "success": not result.degraded,
        "prompts": {
            "original": result.original,
            "sanitized": result.original,
            "compiled": result.output,
            "optimized": result.output,
        },
        "security_result": result.security.to_dict() if result.security else {},
        "routing_decision": default_routing_decision(),
        "optimization_metrics": {
            "token_reduction_percentage": (
                result.metrics.token_reduction_pct if result.metrics else 0
            ),
        },
        "performance_metrics": {
            "total_pipeline_ms": (
                result.metrics.processing_time_ms if result.metrics else 0
            ),
        },
        "stage_metrics": {},
        "degraded": result.degraded,
        "degraded_reason": result.degraded_reason,
    }


def to_legacy_pipeline_dict(result: ProcessResult) -> Dict[str, Any]:
    """Deprecated Pipeline.process() dict shape."""
    return process_result_to_legacy_dict(result)


def timeout_legacy_dict(
    prompt: str, *, timeout_seconds: Optional[float]
) -> Dict[str, Any]:
    """Legacy dict when the processor budget is exceeded."""
    warn_legacy_dict()
    return {
        "success": True,
        "timed_out": True,
        "timeout_stage": "processor",
        "prompts": {
            "original": prompt,
            "sanitized": prompt,
            "compiled": prompt,
            "optimized": prompt,
        },
        "security_result": None,
        "routing_decision": default_routing_decision(),
        "optimization_metrics": {"token_reduction_percentage": 0},
        "performance_metrics": {
            "total_pipeline_ms": 0,
            "timeout_seconds": timeout_seconds,
        },
        "stage_metrics": {},
    }
