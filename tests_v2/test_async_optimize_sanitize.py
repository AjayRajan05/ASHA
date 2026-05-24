"""Async optimize/sanitize tests."""

import asyncio

import pytest

pytest.importorskip("anyio")
pytestmark = pytest.mark.anyio

from privysha import optimize_async, process_async, sanitize_async


async def test_optimize_async_returns_string():
    result = await optimize_async("Summarize quarterly sales data please")
    assert isinstance(result, str)
    assert len(result) > 0


async def test_sanitize_async_masks_email():
    result = await sanitize_async("Contact alice@example.com")
    assert "alice@example.com" not in result


async def test_process_async_fail_safe(monkeypatch):
    async def boom(*args, **kwargs):
        raise RuntimeError("fail")

    import privysha.utils.dropin as dropin

    monkeypatch.setattr(dropin, "_process_async", boom)
    result = await process_async("secret@company.com", privacy=True)
    assert isinstance(result, str)
    assert "secret@company.com" not in result


async def test_optimize_async_return_metrics():
    result = await optimize_async("Hello world", return_metrics=True)
    assert isinstance(result, dict)
    assert result.get("async") is True
    assert "optimized" in result


async def test_optimize_async_privacy_mode_off():
    result = await optimize_async(
        "keep@company.com",
        privacy_mode="off",
        trust_input=True,
        return_metrics=True,
    )
    assert "keep@company.com" in result["optimized"]


async def test_optimize_async_trust_input():
    prompt = "unchanged@company.com"
    result = await optimize_async(prompt, trust_input=True, return_metrics=True)
    assert result["optimized"] == prompt


async def test_optimize_async_fail_safe(monkeypatch):
    async def boom(*args, **kwargs):
        raise RuntimeError("fail")

    import privysha.utils.dropin as dropin

    monkeypatch.setattr(dropin, "_process_async", boom)
    result = await optimize_async("test@company.com", return_metrics=True)
    assert result.get("fallback") is True


async def test_sanitize_async_return_details():
    result = await sanitize_async("a@b.com", return_details=True)
    assert isinstance(result, dict)
    assert "sanitized" in result
    assert result.get("async") is True


async def test_sanitize_async_fail_safe(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("fail")

    import privysha.security.service as svc

    monkeypatch.setattr(svc, "run_security_only", boom)
    result = await sanitize_async("fallback@company.com", return_details=True)
    assert result.get("fallback") is True


async def test_process_async_debug_mode():
    result = await process_async("Hello", return_metrics=True, debug=True)
    assert isinstance(result, dict)
    assert "security_result" in result


async def test_process_async_empty_prompt():
    assert await process_async("") == ""


async def test_process_async_invalid_type():
    assert await process_async(None) == ""


async def test_process_async_concurrent_calls_isolated():
    results = await asyncio.gather(
        process_async("First prompt"),
        process_async("Second prompt"),
    )
    assert len(results) == 2
    assert all(isinstance(r, str) for r in results)
