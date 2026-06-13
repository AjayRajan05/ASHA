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

"""Optional OpenTelemetry integration for stage tracing."""

from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

_otel_enabled = False
_tracer = None


def enable_otel(service_name: str = "privysha") -> bool:
    """
    Enable OpenTelemetry span export for pipeline stages.

    Requires: pip install privysha[otel]
    """
    global _otel_enabled, _tracer
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )

        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        _otel_enabled = True
        return True
    except ImportError:
        return False


@contextmanager
def stage_span(stage_name: str) -> Iterator[Optional[Any]]:
    """Context manager for pipeline stage spans (no-op when OTEL disabled)."""
    if not _otel_enabled or _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(f"privysha.stage.{stage_name}") as span:
        yield span


def trace_stage(stage_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator for ad-hoc stage spans."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with stage_span(stage_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_tracer() -> Optional[Any]:
    return _tracer
