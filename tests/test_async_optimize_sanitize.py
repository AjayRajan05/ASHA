"""Async optimize/sanitize tests."""

import asyncio

import pytest

pytest.importorskip("anyio")
pytestmark = pytest.mark.anyio

from privysha.utils.dropin import optimize_async, process_async, sanitize_async
from privysha.types.results import OptimizeResult, ProcessResult, SanitizeResult
from privysha.utils.dropin_privacy import SECURITY_FAIL_CLOSED_PLACEHOLDER


async def test_optimize_async_returns_optimize_result():
    result = await optimize_async("Summarize quarterly sales data please")
    assert isinstance(result, OptimizeResult)
    assert len(result.output) > 0


async def test_sanitize_async_masks_email():
    result = await sanitize_async("Contact alice@example.com")
    assert isinstance(result, SanitizeResult)
    assert "alice@example.com" not in result.output


async def test_process_async_fail_closed(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("fail")

    import privysha.runtime.processor as proc_mod

    monkeypatch.setattr(proc_mod.PromptProcessor, "_run_engines", boom)
    result = await process_async("secret@company.com", mode="balanced")
    assert isinstance(result, ProcessResult)
    assert result.output == SECURITY_FAIL_CLOSED_PLACEHOLDER or "secret@company.com" not in result.output
    assert result.degraded is True


async def test_optimize_async_trust_input():
    prompt = "unchanged@company.com"
    result = await optimize_async(prompt, trust_input=True)
    assert isinstance(result, OptimizeResult)
    assert result.output == prompt


async def test_sanitize_async_observable_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("fail")

    import privysha.core.engines as engines

    monkeypatch.setattr(engines, "run_security_only", boom)
    result = await sanitize_async("fallback@company.com")
    assert isinstance(result, SanitizeResult)
    assert result.degraded is True
    assert result.safe is False


async def test_process_async_returns_process_result():
    result = await process_async("Hello world")
    assert isinstance(result, ProcessResult)


async def test_process_async_concurrent_calls_isolated():
    results = await asyncio.gather(
        process_async("First prompt"),
        process_async("Second prompt"),
    )
    assert len(results) == 2
    assert all(isinstance(r, ProcessResult) for r in results)
