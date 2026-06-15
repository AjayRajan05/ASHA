"""Django integration tests — Gap 14.

Tests the Django middleware without requiring a full Django project.
Uses the middleware's internal methods directly (no live HTTP needed),
plus the importorskip smoke test for when Django is installed.
"""

import json
import pytest


# ---------------------------------------------------------------------------
# Tests that run without Django installed (test middleware logic only)
# ---------------------------------------------------------------------------


def test_django_middleware_module_importable():
    """The middleware module must be importable even without Django."""
    from privysha.integrations.django import middleware  # noqa: F401

    assert middleware is not None


def test_django_middleware_class_exists():
    from privysha.integrations.django.middleware import PrivySHAMiddleware

    assert PrivySHAMiddleware is not None


def test_django_import_raises_without_django(monkeypatch):
    """Instantiating PrivySHAMiddleware without Django raises ImportError."""
    import privysha.integrations.django.middleware as dj_mod

    monkeypatch.setattr(dj_mod, "DJANGO_AVAILABLE", False)

    with pytest.raises((ImportError, TypeError)):
        # __init__ checks DJANGO_AVAILABLE and raises ImportError
        PrivySHAMiddleware = dj_mod.PrivySHAMiddleware
        PrivySHAMiddleware(get_response=lambda r: r)


# ---------------------------------------------------------------------------
# Tests using mocked Django objects (no Django install required)
# ---------------------------------------------------------------------------


class _MockSettings:
    PRIVYSHA_CONFIG = {
        "PRIVACY": True,
        "TOKEN_BUDGET": 800,
        "ENDPOINTS": ["/api/chat"],
        "DEBUG_MODE": False,
    }


class _MockRequest:
    def __init__(self, path="/api/chat", body=None, method="POST"):
        self.path = path
        self.body = body or b"{}"
        self.method = method
        self.content_type = "application/json"
        self.POST = {}


class _MockResponse:
    def __init__(self):
        self._headers: dict = {}

    def __setitem__(self, key, value):
        self._headers[key] = value

    def __getitem__(self, key):
        return self._headers[key]


def _make_middleware_instance():
    """Build PrivySHAMiddleware skipping the DJANGO_AVAILABLE guard."""
    import privysha.integrations.django.middleware as dj_mod

    # Temporarily pretend Django is available
    orig_flag = dj_mod.DJANGO_AVAILABLE
    dj_mod.DJANGO_AVAILABLE = True
    import privysha.integrations.django.middleware as dj_fresh

    mw = object.__new__(dj_fresh.PrivySHAMiddleware)
    mw.privacy = True
    mw.token_budget = 800
    mw.debug_mode = False
    mw.endpoints = ["/api/chat"]
    mw.prompt_fields = ["prompt", "messages", "input", "content"]
    dj_mod.DJANGO_AVAILABLE = orig_flag
    return mw


def test_should_process_endpoint_match():
    mw = _make_middleware_instance()
    assert mw._should_process_endpoint("/api/chat") is True


def test_should_process_endpoint_no_match():
    mw = _make_middleware_instance()
    assert mw._should_process_endpoint("/health") is False


def test_find_prompts_flat():
    mw = _make_middleware_instance()
    data = {"prompt": "Summarize this", "other": "irrelevant"}
    prompts = mw._find_prompts(data)
    assert any("prompt" in path for path, _ in prompts)
    assert any(text == "Summarize this" for _, text in prompts)


def test_find_prompts_nested_messages():
    mw = _make_middleware_instance()
    data = {
        "messages": [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "Hi"},
        ]
    }
    prompts = mw._find_prompts(data)
    contents = [text for _, text in prompts]
    assert "Hello there" in contents


def test_update_field_simple():
    mw = _make_middleware_instance()
    data = {"prompt": "old value"}
    mw._update_field(data, "prompt", "new value")
    assert data["prompt"] == "new value"


def test_update_field_nested():
    mw = _make_middleware_instance()
    data = {"messages": [{"role": "user", "content": "old"}]}
    mw._update_field(data, "messages[0].content", "new")
    assert data["messages"][0]["content"] == "new"


def test_process_prompts_returns_dict():
    mw = _make_middleware_instance()
    data = {"prompt": "Tell me about AI"}
    processed_data, info = mw._process_prompts(data)
    assert isinstance(processed_data, dict)
    assert info["prompts_processed"] >= 1


def test_get_request_data_json():
    mw = _make_middleware_instance()
    payload = {"prompt": "hello"}
    req = _MockRequest(body=json.dumps(payload).encode())
    result = mw._get_request_data(req)
    assert result == payload


def test_get_request_data_non_post_returns_none():
    mw = _make_middleware_instance()
    req = _MockRequest(method="GET")
    result = mw._get_request_data(req)
    assert result is None


def test_replace_request_data_stores_json():
    mw = _make_middleware_instance()
    req = _MockRequest()
    mw._replace_request_data(req, {"prompt": "processed"})
    assert hasattr(req, "privysha_processed_data")
    assert req.privysha_processed_data["prompt"] == "processed"


# ---------------------------------------------------------------------------
# Smoke test with real Django (skipped if not installed)
# ---------------------------------------------------------------------------


def test_django_middleware_smoke_with_real_django():
    pytest.importorskip("django")
    from privysha.integrations.django.middleware import PrivySHAMiddleware

    assert PrivySHAMiddleware is not None
    assert callable(PrivySHAMiddleware)
