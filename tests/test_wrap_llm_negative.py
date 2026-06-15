"""Negative and fail-safe tests for wrap_llm and wrapper helpers."""

import pytest

from privysha.integrations import wrap_llm
from privysha.exceptions import PrivySHAProcessingError, PrivySHAWrapError
from privysha.integrations.llm_wrap import (
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


def test_dropin_wrap_llm_raises_on_incompatible_client():
    with pytest.raises(ValueError):
        wrap_llm({"not_an_llm": True})


def test_wrap_llm_fail_closed_on_process_error(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("process failed")

    import privysha.integrations.llm_wrap as llm_wrap_mod

    monkeypatch.setattr(llm_wrap_mod, "_process_prompt_for_wrap", boom)
    client = _MockClient()
    wrapped = wrapper_wrap_llm(client)
    with pytest.raises(PrivySHAProcessingError):
        wrapped.chat.completions.create(
            messages=[{"role": "user", "content": "keep@example.com"}],
        )


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


def test_wrap_function_sync_fail_closed(monkeypatch):
    def echo(x):
        return x

    import privysha.utils.dropin as dropin_mod

    def boom(prompt, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(dropin_mod, "process", boom)
    wrapped = wrap_function(echo)
    with pytest.raises(PrivySHAProcessingError):
        wrapped("hello")


def test_safe_wrap_raises_on_failure():
    with pytest.raises(PrivySHAWrapError):
        safe_wrap(object())


def test_auto_wrap_raises_on_failure():
    with pytest.raises(PrivySHAWrapError):
        auto_wrap(object())


def test_universal_wrapper_wrap_method_missing_raises():
    uw = UniversalWrapper()
    with pytest.raises(ValueError, match="not found"):
        uw.wrap_method(object(), "nonexistent_method")
