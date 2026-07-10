# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Runtime observability helpers - no integration-layer imports."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Optional

_otel_enabled = False
_tracer: Optional[Any] = None


def set_tracer(tracer: Any, *, enabled: bool = True) -> None:
    """Register an OpenTelemetry tracer (called from integrations.otel)."""
    global _otel_enabled, _tracer
    _tracer = tracer
    _otel_enabled = enabled and tracer is not None


def is_otel_enabled() -> bool:
    return _otel_enabled and _tracer is not None


@contextmanager
def stage_span(stage_name: str) -> Iterator[Optional[Any]]:
    """Context manager for pipeline stage spans (no-op when OTEL disabled)."""
    if not is_otel_enabled() or _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(f"asha.stage.{stage_name}") as span:
        yield span
