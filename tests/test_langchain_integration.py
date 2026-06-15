"""LangChain integration tests — Gap 15.

Tests the LangChain integration module.  Tests that require LangChain to be
installed are guarded with pytest.importorskip so they are skipped in
environments without the [langchain] extra.  Tests of the module structure
itself (importability, public API surface) run without any extra installs.
"""

import pytest

from privysha.utils.dropin import process


# ---------------------------------------------------------------------------
# Module structure tests (no LangChain required)
# ---------------------------------------------------------------------------


def test_langchain_wrapper_module_importable():
    from privysha.integrations.langchain import wrapper  # noqa: F401

    assert wrapper is not None


def test_langchain_wrapper_exports_expected_symbols():
    import privysha.integrations.langchain.wrapper as lc_mod

    assert hasattr(lc_mod, "PrivySHAPromptTemplate")
    assert hasattr(lc_mod, "PrivySHARunnable")
    assert hasattr(lc_mod, "wrap_runnable")
    assert hasattr(lc_mod, "wrap_llm_chain")
    assert hasattr(lc_mod, "wrap_prompt_template")


# ---------------------------------------------------------------------------
# PrivySHARunnable: works without LangChain because it subclasses a stub
# ---------------------------------------------------------------------------


def test_privysha_runnable_invoke_string_input():
    from privysha.integrations.langchain.wrapper import PrivySHARunnable

    outputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            outputs.append(inp)
            return f"result:{inp}"

    runnable = PrivySHARunnable(
        runnable=_FakeRunnable(),
        privacy=False,
        token_budget=1200,
        input_key="input",
    )
    result = runnable.invoke("Hello, world!")
    assert result.startswith("result:")
    assert outputs  # runnable was called


def test_privysha_runnable_invoke_dict_input():
    from privysha.integrations.langchain.wrapper import PrivySHARunnable

    outputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            outputs.append(inp)
            return f"result:{inp}"

    runnable = PrivySHARunnable(
        runnable=_FakeRunnable(),
        privacy=False,
        input_key="input",
    )
    result = runnable.invoke({"input": "Summarize this"})
    assert "result:" in str(result)


def test_privysha_runnable_masks_pii_in_dict():
    from privysha.integrations.langchain.wrapper import PrivySHARunnable

    processed_inputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            processed_inputs.append(inp)
            return "ok"

    runnable = PrivySHARunnable(
        runnable=_FakeRunnable(),
        privacy=True,
        input_key="input",
    )
    runnable.invoke({"input": "Contact alice@example.com now"})
    assert processed_inputs
    # Email should be masked before reaching the inner runnable
    assert "alice@example.com" not in str(processed_inputs[0])


def test_privysha_runnable_passthrough_unknown_input():
    """Non-string, non-dict inputs should pass through unchanged."""
    from privysha.integrations.langchain.wrapper import PrivySHARunnable

    outputs = []

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            outputs.append(inp)
            return inp

    runnable = PrivySHARunnable(runnable=_FakeRunnable(), input_key="input")
    runnable.invoke(42)  # integer — pass through
    assert outputs[0] == 42


def test_privysha_runnable_debug_metrics():
    from privysha.integrations.langchain.wrapper import PrivySHARunnable

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            return "done"

    runnable = PrivySHARunnable(
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


def test_wrap_runnable_returns_privysha_runnable():
    from privysha.integrations.langchain.wrapper import (
        PrivySHARunnable,
        wrap_runnable,
    )

    class _FakeRunnable:
        def invoke(self, inp, config=None):
            return inp

    wrapped = wrap_runnable(_FakeRunnable(), privacy=False)
    assert isinstance(wrapped, PrivySHARunnable)


# ---------------------------------------------------------------------------
# PrivySHAPromptTemplate: only when LangChain is installed
# ---------------------------------------------------------------------------


def test_privysha_prompt_template_requires_langchain():
    import privysha.integrations.langchain.wrapper as lc_mod

    if lc_mod.LANGCHAIN_AVAILABLE:
        from privysha.integrations.langchain.wrapper import PrivySHAPromptTemplate

        tpl = PrivySHAPromptTemplate(
            input_variables=["query"],
            template="Answer: {query}",
            privacy=False,
        )
        result = tpl.format(query="What is 2+2?")
        assert isinstance(result, str)
    else:
        # Without LangChain, attempting to instantiate raises ImportError
        from privysha.integrations.langchain.wrapper import PrivySHAPromptTemplate

        with pytest.raises(ImportError):
            PrivySHAPromptTemplate(
                input_variables=["query"],
                template="Answer: {query}",
                privacy=False,
            )


# ---------------------------------------------------------------------------
# Smoke test with real LangChain (skipped if not installed)
# ---------------------------------------------------------------------------


def test_langchain_full_smoke():
    pytest.importorskip("langchain_core")
    import privysha.integrations.langchain.wrapper as lc_mod

    assert lc_mod.LANGCHAIN_AVAILABLE is True
