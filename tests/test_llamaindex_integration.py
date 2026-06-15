"""LlamaIndex integration tests — Gap 18.

Tests the LlamaIndex plugin module.  wrap_query_engine and related utilities
are tested via mock objects; the actual llama_index package is optional.
"""

import pytest

from privysha.utils.dropin import process


# ---------------------------------------------------------------------------
# Module structure tests (no LlamaIndex required)
# ---------------------------------------------------------------------------


def test_llamaindex_plugin_importable():
    from privysha.integrations.llamaindex import plugin  # noqa: F401

    assert plugin is not None


def test_llamaindex_plugin_exports_wrap_query_engine():
    from privysha.integrations.llamaindex.plugin import wrap_query_engine

    assert callable(wrap_query_engine)


def test_llamaindex_plugin_exports_privysha_llm():
    from privysha.integrations.llamaindex.plugin import PrivySHALLM

    assert PrivySHALLM is not None


# ---------------------------------------------------------------------------
# wrap_query_engine: mock query engine (no LlamaIndex install needed)
# ---------------------------------------------------------------------------


def test_wrap_query_engine_returns_wrapped():
    from privysha.integrations.llamaindex.plugin import wrap_query_engine

    responses = []

    class _MockQueryEngine:
        def query(self, query_str: str):
            responses.append(query_str)
            return f"result:{query_str}"

    qe = _MockQueryEngine()
    wrapped = wrap_query_engine(qe, privacy=False)
    assert wrapped is not None


def _make_query_bundle(query_str: str):
    """Create a minimal QueryBundle-compatible object (works with or without llama_index)."""
    class _QueryBundle:
        def __init__(self, qs):
            self.query_str = qs
            self.custom_embedding_strs = None
            self.embedding_strs = None
    return _QueryBundle(query_str)


def test_wrap_query_engine_processes_query():
    """Requires llama_index for the QueryBundle reconstruction inside the plugin."""
    pytest.importorskip("llama_index.core")
    from privysha.integrations.llamaindex.plugin import wrap_query_engine
    from llama_index.core.schema import QueryBundle

    received = []

    class _MockQueryEngine:
        def query(self, bundle):
            received.append(bundle.query_str)
            return f"response to: {bundle.query_str}"

    qe = _MockQueryEngine()
    wrapped = wrap_query_engine(qe, privacy=False)
    result = wrapped.query(QueryBundle(query_str="What is 2+2?"))
    assert "response to" in str(result)


def test_wrap_query_engine_masks_pii():
    """PII in queries should be masked — requires llama_index for QueryBundle."""
    pytest.importorskip("llama_index.core")
    from privysha.integrations.llamaindex.plugin import wrap_query_engine
    from llama_index.core.schema import QueryBundle

    received = []

    class _MockQueryEngine:
        def query(self, bundle):
            received.append(bundle.query_str)
            return f"result:{bundle.query_str}"

    qe = _MockQueryEngine()
    wrapped = wrap_query_engine(qe, privacy=True)
    wrapped.query(QueryBundle(query_str="Find documents about user@example.com"))
    assert received
    assert "user@example.com" not in received[0]


# ---------------------------------------------------------------------------
# Smoke test with real LlamaIndex (skipped if not installed)
# ---------------------------------------------------------------------------


def test_llamaindex_real_import_smoke():
    pytest.importorskip("llama_index")
    from privysha.integrations.llamaindex.plugin import wrap_query_engine

    assert callable(wrap_query_engine)
