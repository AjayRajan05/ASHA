"""LangChain integration tests - Gap 15.

Tests the LangChain integration module.  Tests that require LangChain to be
installed are guarded with pytest.importorskip so they are skipped in
environments without the [langchain] extra.  Tests of the module structure
itself (importability, public API surface) run without any extra installs.
"""

import pytest

from asha.utils.dropin import process


# ---------------------------------------------------------------------------
# Module structure tests (no LangChain required)
# ---------------------------------------------------------------------------


def test_langchain_wrapper_module_importable():
    from asha.integrations.langchain import wrapper  # noqa: F401

    assert wrapper is not None


def test_langchain_wrapper_exports_expected_symbols():
    import asha.integrations.langchain.wrapper as lc_mod

    assert hasattr(lc_mod, "ASHAPromptTemplate")
    assert hasattr(lc_mod, "ASHARunnable")
    assert hasattr(lc_mod, "wrap_runnable")
    assert hasattr(lc_mod, "wrap_llm_chain")
    assert hasattr(lc_mod, "wrap_prompt_template")


# ---------------------------------------------------------------------------
# ASHARunnable: works without LangChain because it subclasses a stub
# ---------------------------------------------------------------------------


def test_asha_runnable_invoke_string_input():
    from asha.integrations.langchain.wrapper import ASHARunnable

    outputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            outputs.append(inp)
            return f"result:{inp}"

    runnable = ASHARunnable(
        runnable=_FakeRunnable(),
        privacy=False,
        token_budget=1200,
        input_key="input",
    )
    result = runnable.invoke("Hello, world!")
    assert result.startswith("result:")
    assert outputs  # runnable was called


def test_asha_runnable_invoke_dict_input():
    from asha.integrations.langchain.wrapper import ASHARunnable

    outputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            outputs.append(inp)
            return f"result:{inp}"

    runnable = ASHARunnable(
        runnable=_FakeRunnable(),
        privacy=False,
        input_key="input",
    )
    result = runnable.invoke({"input": "Summarize this"})
    assert "result:" in str(result)


def test_asha_runnable_masks_pii_in_dict():
    from asha.integrations.langchain.wrapper import ASHARunnable

    processed_inputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            processed_inputs.append(inp)
            return "ok"

    runnable = ASHARunnable(
        runnable=_FakeRunnable(),
        privacy=True,
        input_key="input",
    )
    runnable.invoke({"input": "Contact alice@example.com now"})
    assert processed_inputs
    # Email should be masked before reaching the inner runnable
    assert "alice@example.com" not in str(processed_inputs[0])


def test_asha_runnable_passthrough_unknown_input():
    """Non-string, non-dict inputs should pass through unchanged."""
    from asha.integrations.langchain.wrapper import ASHARunnable

    outputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            outputs.append(inp)
            return inp

    runnable = ASHARunnable(runnable=_FakeRunnable(), input_key="input")
    runnable.invoke(42)  # integer - pass through
    assert outputs[0] == 42


def test_asha_runnable_debug_metrics():
    from asha.integrations.langchain.wrapper import ASHARunnable

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            return "done"

    runnable = ASHARunnable(
        runnable=_FakeRunnable(),
        privacy=False,
        debug_metrics=True,
    )
    runnable.invoke("Analyze dataset")
    metrics = runnable.get_last_metrics()
    assert metrics is not None
    assert "optimized" in metrics


# ---------------------------------------------------------------------------
# wrap_runnable convenience function
# ---------------------------------------------------------------------------


def test_wrap_runnable_returns_asha_runnable():
    from asha.integrations.langchain.wrapper import (
        ASHARunnable,
        wrap_runnable,
    )

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            return inp

    wrapped = wrap_runnable(_FakeRunnable(), privacy=False)
    assert isinstance(wrapped, ASHARunnable)


# ---------------------------------------------------------------------------
# ASHAPromptTemplate: only when LangChain is installed
# ---------------------------------------------------------------------------


def test_asha_prompt_template_requires_langchain():
    import asha.integrations.langchain.wrapper as lc_mod

    if lc_mod.LANGCHAIN_AVAILABLE:
        from asha.integrations.langchain.wrapper import ASHAPromptTemplate

        tpl = ASHAPromptTemplate(
            input_variables=["query"],
            template="Answer: {query}",
            privacy=False,
        )
        result = tpl.format(query="What is 2+2?")
        assert isinstance(result, str)
    else:
        # Without LangChain, attempting to instantiate raises ImportError
        from asha.integrations.langchain.wrapper import ASHAPromptTemplate

        with pytest.raises(ImportError):
            ASHAPromptTemplate(
                input_variables=["query"],
                template="Answer: {query}",
                privacy=False,
            )


# ---------------------------------------------------------------------------
# Smoke test with real LangChain (skipped if not installed)
# ---------------------------------------------------------------------------


def test_langchain_full_smoke():
    pytest.importorskip("langchain_core")
    import asha.integrations.langchain.wrapper as lc_mod

    assert lc_mod.LANGCHAIN_AVAILABLE is True
