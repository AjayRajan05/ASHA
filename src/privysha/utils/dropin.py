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

"""
Drop-in utility functions (NEW - CRITICAL FOR ADOPTION)
from .dropin import process, optimize, sanitize

These functions provide the CRITICAL adoption path:
- process() - One-line prompt processing
- optimize() - Token optimization only
- sanitize() - Security only
"""

from __future__ import annotations

from typing import Optional

import difflib

from ..core.policy_config import PolicyConfig
from ..core.safety import safety_mode_from_policy_mode
from ..runtime.processor import PromptProcessor
from ..runtime.resolve import resolve_process_call, resolve_sanitize_policy
from ..types.results import OptimizeResult, ProcessResult, SanitizeResult
from .dropin_helpers import coerce_process_output

# Re-export for backward compatibility
_coerce_process_output = coerce_process_output


def generate_text_diff(original: str, modified: str) -> str:
    """Generate a readable diff between original and modified text."""
    if original == modified:
        return "No changes made"

    diff_lines = list(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile="original",
            tofile="modified",
            lineterm="",
        )
    )

    if not diff_lines:
        return "No changes made"

    return "\n".join(diff_lines)


def process(
    prompt: str,
    mode: str = "balanced",
    *,
    policy: Optional[PolicyConfig] = None,
    token_budget: int = 1200,
    trace: bool = False,
    debug: bool = False,
    max_retries: int = 0,
    timeout_seconds: Optional[float] = None,
    verbose: bool = False,
    log_level: str = "INFO",
    log_output: str = "console",
    log_file: Optional[str] = None,
    include_legacy_detail: bool = False,
) -> ProcessResult:
    """
    Process a prompt through PrivySHA.

    Most callers only need ``mode`` (``strict``, ``balanced``, ``lite``, ``off``).
    Advanced configuration: ``policy=PolicyConfig(...)``.
    """
    context, runtime_extras = resolve_process_call(
        mode=mode,
        policy=policy,
        token_budget=token_budget,
        trace=trace,
        debug=debug,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        verbose=verbose,
        log_level=log_level,
        log_output=log_output,
        log_file=log_file,
        include_legacy_detail=include_legacy_detail,
    )

    return PromptProcessor().run_with_context(
        prompt,
        context,
        **runtime_extras,
    )


async def process_async(
    prompt: str,
    mode: str = "balanced",
    *,
    policy: Optional[PolicyConfig] = None,
    token_budget: int = 1200,
    trace: bool = False,
    debug: bool = False,
    max_retries: int = 0,
    timeout_seconds: Optional[float] = None,
    verbose: bool = False,
    log_level: str = "INFO",
    log_output: str = "console",
    log_file: Optional[str] = None,
    include_legacy_detail: bool = False,
) -> ProcessResult:
    """Async process — returns ProcessResult."""
    import asyncio

    return await asyncio.to_thread(
        process,
        prompt,
        mode=mode,
        policy=policy,
        token_budget=token_budget,
        trace=trace,
        debug=debug,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        verbose=verbose,
        log_level=log_level,
        log_output=log_output,
        log_file=log_file,
        include_legacy_detail=include_legacy_detail,
    )


async def optimize_async(
    prompt: str,
    token_budget: int = 1200,
    trust_input: bool = False,
) -> OptimizeResult:
    """Async tokens-only optimization."""
    import asyncio
    from ..core.engines import optimize_tokens

    if trust_input:
        from ..types.results import MetricsInfo
        return OptimizeResult(
            output=prompt,
            original=prompt,
            degraded=False,
            degraded_reason=None,
            metrics=MetricsInfo(0, 0.0, 0.0),
        )
    return await asyncio.to_thread(optimize_tokens, prompt, token_budget=token_budget)


async def sanitize_async(
    prompt: str,
    *,
    mode: str = "balanced",
    policy: Optional[PolicyConfig] = None,
    max_retries: int = 0,
    timeout_seconds: Optional[float] = None,
) -> SanitizeResult:
    """Async sanitize — observable failure on detector errors."""
    import asyncio
    from ..core.engines import sanitize_text

    safety, reversible = resolve_sanitize_policy(mode, policy)
    return await asyncio.to_thread(
        sanitize_text,
        prompt,
        reversible=reversible,
        safety_mode=safety,
        mode=mode,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
    )


def optimize(
    prompt: str,
    token_budget: int = 1200,
    trust_input: bool = False,
) -> OptimizeResult:
    """Token optimization only via MSDPC — no security or compile stages."""
    from ..core.engines import optimize_tokens

    if trust_input:
        from ..types.results import MetricsInfo
        return OptimizeResult(
            output=prompt,
            original=prompt,
            degraded=False,
            degraded_reason=None,
            metrics=MetricsInfo(0, 0.0, 0.0),
        )
    return optimize_tokens(prompt, token_budget=token_budget)


def sanitize(
    prompt: str,
    *,
    mode: str = "balanced",
    policy: Optional[PolicyConfig] = None,
    max_retries: int = 0,
    timeout_seconds: Optional[float] = None,
) -> SanitizeResult:
    """
    Sanitize a prompt for security only (PII masking, threat detection).

    Use ``mode="strict"`` to block on failure; ``mode="balanced"`` for degraded fallback.
    Advanced: ``policy=PolicyConfig(reversible=True)``.
    """
    from ..core.engines import sanitize_text

    safety, reversible = resolve_sanitize_policy(mode, policy)
    return sanitize_text(
        prompt,
        reversible=reversible,
        safety_mode=safety,
        mode=mode,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
    )
