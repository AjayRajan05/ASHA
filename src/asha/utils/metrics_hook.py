# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Best-effort metrics recording for the process() hot path."""

from typing import Any, Dict, List, Union


def _count_pii(pii_detected: Union[List[str], int, None]) -> int:
    if pii_detected is None:
        return 0
    if isinstance(pii_detected, int):
        return pii_detected
    return len(pii_detected)


def record_process_metrics(
    *,
    prompt: str,
    optimized: str,
    latency_ms: float,
    success: bool = True,
    tokens_saved: int = 0,
    threats_blocked: int = 0,
    pii_detected: Union[List[str], int, None] = None,
) -> None:
    """Record one process() invocation in the global MetricsDashboard (never raises)."""
    try:
        from ..core.metrics_dashboard import record_request

        tokens_processed = max(len(str(prompt).split()), 1)
        record_request(
            latency_ms=float(latency_ms or 0),
            tokens_processed=tokens_processed,
            tokens_saved=max(int(tokens_saved or 0), 0),
            success=success,
            threats_blocked=max(int(threats_blocked or 0), 0),
            pii_detected=_count_pii(pii_detected),
        )
    except Exception:
        pass


def record_from_pipeline_result(
    prompt: str,
    result: Dict[str, Any],
    *,
    success: bool = True,
) -> None:
    """Derive dashboard metrics from a pipeline result dict."""
    perf = result.get("performance_metrics") or {}
    latency_ms = perf.get("total_pipeline_ms", 0)
    optimized = (result.get("prompts") or {}).get("optimized") or prompt

    opt_metrics = result.get("optimization_metrics") or {}
    original_tokens = max(len(str(prompt).split()), 1)
    optimized_tokens = max(len(str(optimized).split()), 1)
    tokens_saved = max(original_tokens - optimized_tokens, 0)

    security = result.get("security_result")
    threats = 0
    pii_count = 0
    if isinstance(security, dict):
        threats = len(security.get("detected_threats") or [])
        entities = security.get("masked_entities") or {}
        pii_count = len(entities) if isinstance(entities, dict) else 0
    elif security is not None:
        threats = len(getattr(security, "detected_threats", []) or [])
        entities = getattr(security, "masked_entities", {}) or {}
        pii_count = len(entities) if isinstance(entities, dict) else 0

    record_process_metrics(
        prompt=prompt,
        optimized=optimized,
        latency_ms=latency_ms,
        success=success and result.get("success", True),
        tokens_saved=tokens_saved or int(opt_metrics.get("tokens_saved", 0) or 0),
        threats_blocked=threats,
        pii_detected=pii_count,
    )
