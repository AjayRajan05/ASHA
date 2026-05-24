"""Async and streaming behavior tests (no live API keys)."""

import pytest

pytest.importorskip("anyio")
pytestmark = pytest.mark.anyio

from privysha.core.streaming import (
    handle_streaming_response,
    handle_async_streaming_response,
    is_streaming_response,
)
from privysha.utils.dropin import process_async, sanitize_async
from privysha.utils.wrapper import wrap_llm


class _AsyncCompletions:
    async def create(self, messages, **kwargs):
        if kwargs.get("stream"):

            async def gen():
                for part in ("Hello", " ", "world"):
                    yield part

            return gen()

        return type(
            "Response",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type(
                                "Message",
                                (),
                                {"content": messages[-1]["content"]},
                            )()
                        },
                    )()
                ]
            },
        )()


class MockStreamClient:
    """Fresh chat/completions per instance so wrap_llm does not leak state."""

    def __init__(self):
        self.chat = type("Chat", (), {"completions": _AsyncCompletions()})()


async def test_sanitize_async_masks_email():
    out = await sanitize_async("Contact john@example.com")
    assert isinstance(out, str)
    assert "john@example.com" not in out


async def test_process_async_returns_string():
    out = await process_async("Summarize quarterly sales trends.")
    assert isinstance(out, str)
    assert len(out) > 0


async def test_process_async_return_metrics():
    out = await process_async("Email: a@b.com", return_metrics=True)
    assert isinstance(out, dict)
    assert "optimized" in out
    assert out.get("async") is True


def test_sync_streaming_passthrough():
    chunks = list(handle_streaming_response(iter(["a", "b", "c"])))
    assert chunks == ["a", "b", "c"]
    assert is_streaming_response(iter(["x"])) is True


async def test_async_streaming_passthrough():
    async def stream():
        for part in ("x", "y"):
            yield part

    chunks = []
    async for chunk in handle_async_streaming_response(stream()):
        chunks.append(chunk)
    assert chunks == ["x", "y"]


async def test_wrap_llm_async_streaming():
    client = MockStreamClient()
    wrapped = wrap_llm(client)
    response = await wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "john@example.com"}],
        stream=True,
    )
    chunks = []
    async for chunk in response:
        chunks.append(chunk)
    assert chunks == ["Hello", " ", "world"]


class _SyncCompletions:
    def create(self, messages, **kwargs):
        if kwargs.get("stream"):
            return iter(["chunk1", "chunk2"])

        return type(
            "Response",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type(
                                "Message",
                                (),
                                {"content": messages[-1]["content"]},
                            )()
                        },
                    )()
                ]
            },
        )()


class MockSyncStreamClient:
    """Fresh chat/completions per instance so wrap_llm does not leak state."""

    def __init__(self):
        self.chat = type("Chat", (), {"completions": _SyncCompletions()})()


def test_wrap_llm_sync_streaming():
    client = MockSyncStreamClient()
    wrapped = wrap_llm(client)
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "stream test"}],
        stream=True,
    )
    assert list(response) == ["chunk1", "chunk2"]


def test_wrap_llm_forwards_privacy_and_budget():
    client = MockSyncStreamClient()
    wrapped = wrap_llm(client, privacy=False, token_budget=500, mode="off")
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "keep@example.com intact"}],
    )
    content = response.choices[0].message.content
    assert "keep@example.com" in content


def test_streaming_does_not_buffer_chunks():
    from privysha.core.streaming import handle_streaming_response

    chunks = list(handle_streaming_response(iter(["a", "b", "c"])))
    assert chunks == ["a", "b", "c"]


def test_wrap_llm_sync_streaming_fail_safe_on_process_error(monkeypatch):
    import privysha.utils.wrapper as wrapper_mod

    def boom(*args, **kwargs):
        raise RuntimeError("process failed")

    monkeypatch.setattr(wrapper_mod, "_process_prompt_for_wrap", boom)
    client = MockSyncStreamClient()
    wrapped = wrap_llm(client)
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "stream@test.com"}],
        stream=True,
    )
    assert list(response) == ["chunk1", "chunk2"]
