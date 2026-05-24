"""Negative and fail-safe tests for wrap_llm and wrapper helpers."""

import pytest

from privysha import wrap_llm
from privysha.utils.wrapper import (
    wrap_llm as wrapper_wrap_llm,
    safe_wrap,
    auto_wrap,
    wrap_function,
    UniversalWrapper,
)


class _SyncCompletions:
    def create(self, messages, **kwargs):
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


class _MockClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": _SyncCompletions()})()


def test_dropin_wrap_llm_raises_when_client_is_none():
    with pytest.raises(ValueError, match="cannot be None"):
        wrap_llm(None)


def test_wrapper_wrap_llm_raises_on_incompatible_client():
    with pytest.raises(ValueError, match="Could not find compatible"):
        wrapper_wrap_llm(object())


def test_dropin_wrap_llm_returns_original_on_incompatible_client():
    client = {"not_an_llm": True}
    result = wrap_llm(client)
    assert result is client


def test_wrap_llm_fail_safe_preserves_prompt_on_process_error(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("process failed")

    import privysha.utils.wrapper as wrapper_mod

    monkeypatch.setattr(wrapper_mod, "_process_prompt_for_wrap", boom)
    client = _MockClient()
    wrapped = wrapper_wrap_llm(client)
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "keep@example.com"}],
    )
    assert "keep@example.com" in response.choices[0].message.content


def test_wrap_llm_strict_mode_masks_pii():
    client = _MockClient()
    wrapped = wrap_llm(client, mode="strict")
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "Email secret@company.com"}],
    )
    content = response.choices[0].message.content
    assert "secret@company.com" not in content


def test_wrap_llm_lite_mode_processes_without_crash():
    client = _MockClient()
    wrapped = wrap_llm(client, mode="lite")
    response = wrapped.chat.completions.create(
        messages=[{"role": "user", "content": "Summarize sales data."}],
    )
    assert len(response.choices[0].message.content) > 0


def test_wrap_function_sync_fail_safe(monkeypatch):
    def echo(x):
        return x

    import privysha.utils.dropin as dropin_mod

    def boom(prompt, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(dropin_mod, "process", boom)
    wrapped = wrap_function(echo)
    assert wrapped("hello") == "hello"


def test_safe_wrap_returns_original_on_failure():
    result = safe_wrap(object())
    assert result is not None


def test_auto_wrap_keeps_failed_clients():
    good = _MockClient()
    bad = object()
    wrapped = auto_wrap(good, bad)
    assert len(wrapped) == 2
    assert wrapped[0] is good
    assert wrapped[1] is bad


def test_universal_wrapper_wrap_method_missing_raises():
    uw = UniversalWrapper()
    with pytest.raises(ValueError, match="not found"):
        uw.wrap_method(object(), "nonexistent_method")
