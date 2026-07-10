# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Build typed results from pipeline and security outputs."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..types.results import MetricsInfo, ProcessResult, SanitizeResult, SecurityInfo
from .dropin_privacy import build_security_summary, extract_pii_types, security_field


def build_metrics(
    *,
    prompt: str,
    output: str,
    pipeline_result: Optional[Dict[str, Any]],
    privacy: bool,
    security_result: Any,
) -> MetricsInfo:
    original_tokens = len(prompt.split()) * 1.3
    optimized_tokens = len(output.split()) * 1.3
    tokens_saved = int(original_tokens - optimized_tokens)
    opt_metrics = (pipeline_result or {}).get("optimization_metrics") or {}
    perf = (pipeline_result or {}).get("performance_metrics") or {}
    processing_time = float(perf.get("total_pipeline_ms", 0))

    original_cost = (original_tokens / 1000) * 0.000075
    optimized_cost = (optimized_tokens / 1000) * 0.000075
    cost_pct = (
        ((original_cost - optimized_cost) / original_cost) * 100
        if original_cost > 0
        else 0
    )

    pii_types = extract_pii_types(
        security_result, prompt, privacy, processed_text=output
    )
    detected_threats = security_field(security_result, "detected_threats", []) or []
    threats_count = len(detected_threats)
    if threats_count > 2:
        risk_level = "high"
    elif threats_count > 0:
        risk_level = "medium"
    else:
        risk_level = "low"

    return MetricsInfo(
        tokens_saved=tokens_saved,
        token_reduction_pct=float(opt_metrics.get("token_reduction_percentage", 0)),
        processing_time_ms=processing_time,
        cost_reduction=f"{cost_pct:.1f}%",
        pii_detected=pii_types,
        risk_level=risk_level,
        threats_blocked=threats_count,
        extra={
            "security_score": 100 - (threats_count * 10),
            "optimization_score": min(
                100, float(opt_metrics.get("token_reduction_percentage", 0)) * 2
            ),
        },
    )


def build_process_result(
    *,
    output: str,
    original: str,
    degraded: bool,
    degraded_reason: Optional[str],
    privacy_applied: bool,
    pipeline_result: Optional[Dict[str, Any]],
    privacy: bool,
    include_metrics: bool = True,
    trace: Optional[Dict[str, Any]] = None,
    diff: Optional[str] = None,
    debug: Optional[Dict[str, Any]] = None,
    legacy_detail: Optional[Dict[str, Any]] = None,
) -> ProcessResult:
    security_result = (pipeline_result or {}).get("security_result")
    summary = build_security_summary(security_result)
    security = SecurityInfo.from_summary(summary)
    metrics = (
        build_metrics(
            prompt=original,
            output=output,
            pipeline_result=pipeline_result,
            privacy=privacy,
            security_result=security_result,
        )
        if include_metrics
        else None
    )
    return ProcessResult(
        output=output,
        original=original,
        degraded=degraded,
        degraded_reason=degraded_reason,
        privacy_applied=privacy_applied,
        security=security,
        metrics=metrics,
        trace=trace,
        diff=diff,
        debug=debug,
        legacy_detail=legacy_detail,
    )


def build_sanitize_result(
    *,
    output: str,
    original: str,
    safe: bool,
    degraded: bool,
    degraded_reason: Optional[str],
    security_result: Any,
) -> SanitizeResult:
    if security_result is None:
        security = SecurityInfo(
            safe=safe,
            pii_detected=[],
            threats=[],
            masked_entities={},
        )
    else:
        summary = build_security_summary(security_result)
        if degraded:
            summary["is_safe"] = safe
        security_info = SecurityInfo.from_summary(summary)
        if security_info is None:
            security = SecurityInfo(
                safe=safe,
                pii_detected=[],
                threats=[],
                masked_entities={},
            )
        else:
            security = security_info
    return SanitizeResult(
        output=output,
        original=original,
        safe=safe,
        degraded=degraded,
        degraded_reason=degraded_reason,
        security=security,
    )
