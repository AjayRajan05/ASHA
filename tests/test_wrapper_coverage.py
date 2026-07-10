"""Additional tests for utils/wrapper.py - improves coverage from ~47% toward 70%+."""

import pytest


# ---------------------------------------------------------------------------
# Helpers - lightweight mock clients
# ---------------------------------------------------------------------------


class _SyncClient:
    """Simple sync client with a .generate() method."""

    def __init__(self, response="ok"):
        self._response = response
        self.last_kwargs: dict = {}

    def generate(self, **kwargs):
        self.last_kwargs = kwargs
        return self._response


class _AsyncClient:
    """Simple async client with a .generate() coroutine."""

    def __init__(self, response="async-ok"):
        self._response = response
        self.last_kwargs: dict = {}

    async def generate(self, **kwargs):
        self.last_kwargs = kwargs
        return self._response


class _OpenAIStyleClient:
    """Minimal OpenAI-style client with chat.completions.create."""

    class _Completions:
        def __init__(self):
            self.last_kwargs: dict = {}

        def create(self, **kwargs):
            self.last_kwargs = kwargs
            return {"choices": [{"message": {"content": "reply"}}]}

    class _Chat:
        def __init__(self):
            self.completions = _OpenAIStyleClient._Completions()

    def __init__(self):
        self.chat = _OpenAIStyleClient._Chat()


# ---------------------------------------------------------------------------
# _process_prompt_for_wrap
# ---------------------------------------------------------------------------


def test_process_prompt_for_wrap_strict():
    from asha.integrations.llm_wrap import _process_prompt_for_wrap

    result = _process_prompt_for_wrap("Contact john@example.com", mode="strict")
    assert isinstance(result, str)
    # PII should be masked or removed in strict mode
    assert "@" not in result or "example.com" not in result


def test_process_prompt_for_wrap_balanced():
    from asha.integrations.llm_wrap import _process_prompt_for_wrap

    result = _process_prompt_for_wrap("Summarize quarterly report", mode="balanced")
    assert isinstance(result, str)


def test_process_prompt_for_wrap_lite():
    from asha.integrations.llm_wrap import _process_prompt_for_wrap

    result = _process_prompt_for_wrap("Hello there", mode="lite")
    assert isinstance(result, str)


def test_process_prompt_for_wrap_off():
    from asha.integrations.llm_wrap import _process_prompt_for_wrap

    result = _process_prompt_for_wrap("Hello there", mode="off")
    assert isinstance(result, str)


def test_process_prompt_for_wrap_mode_off():
    from asha.integrations.llm_wrap import _process_prompt_for_wrap

    result = _process_prompt_for_wrap("Hello there", mode="off")
    assert isinstance(result, str)


def test_process_prompt_for_wrap_balanced():
    from asha.integrations.llm_wrap import _process_prompt_for_wrap

    result = _process_prompt_for_wrap("Hello there", mode="balanced")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# _find_generation_method
# ---------------------------------------------------------------------------


def test_find_generation_method_generate():
    from asha.integrations.llm_wrap import _find_generation_method

    client = _SyncClient()
    assert _find_generation_method(client) == "generate"


def test_find_generation_method_create():
    from asha.integrations.llm_wrap import _find_generation_method

    class _Client:
        def create(self, **kwargs):
            return {}

    assert _find_generation_method(_Client()) == "create"


def test_find_generation_method_none():
    from asha.integrations.llm_wrap import _find_generation_method

    class _NoMethodClient:
        pass

    assert _find_generation_method(_NoMethodClient()) is None


# ---------------------------------------------------------------------------
# wrap_llm - sync path
# ---------------------------------------------------------------------------


def test_wrap_llm_sync_client_returns_client():
    from asha.integrations.llm_wrap import wrap_llm

    client = _SyncClient()
    wrapped = wrap_llm(client, mode="balanced")
    assert wrapped is client


def test_wrap_llm_sync_client_calls_generate():
    from asha.integrations.llm_wrap import wrap_llm

    client = _SyncClient(response="result")
    wrap_llm(client, mode="off")
    response = client.generate(prompt="Hello, world!")
    assert response == "result"


def test_wrap_llm_openai_style_nested():
    from asha.integrations.llm_wrap import wrap_llm

    client = _OpenAIStyleClient()
    wrapped = wrap_llm(client, mode="balanced")
    assert wrapped is client
    # Calling create should still work
    result = client.chat.completions.create(
        messages=[{"role": "user", "content": "Summarize this"}]
    )
    assert result is not None


def test_wrap_llm_raises_for_no_method():
    from asha.integrations.llm_wrap import wrap_llm

    class _Empty:
        pass

    with pytest.raises(ValueError, match="Could not find compatible generation method"):
        wrap_llm(_Empty())


def test_wrap_llm_fail_closed_on_process_error(monkeypatch):
    """If _process_prompt_for_wrap raises with privacy on, call must fail closed."""
    from asha.exceptions import ASHAProcessingError
    import asha.integrations.llm_wrap as wrapper

    def boom(prompt, mode, **kwargs):
        raise RuntimeError("simulated process failure")

    monkeypatch.setattr(wrapper, "_process_prompt_for_wrap", boom)

    client = _SyncClient(response="safe-response")
    from asha.integrations import wrap_llm
    wrap_llm(client, mode="balanced")
    with pytest.raises(ASHAProcessingError):
        client.generate(prompt="some prompt")


# ---------------------------------------------------------------------------
# wrap_llm - async path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wrap_llm_async_client():
    from asha.integrations.llm_wrap import wrap_llm

    client = _AsyncClient(response="async-result")
    wrap_llm(client, mode="balanced")
    result = await client.generate(prompt="Hello async")
    assert result == "async-result"


# ---------------------------------------------------------------------------
# wrap_function
# ---------------------------------------------------------------------------


def test_wrap_function_sync():
    from asha.integrations.llm_wrap import wrap_function

    def my_llm(prompt: str) -> str:
        return f"response:{prompt}"

    wrapped = wrap_function(my_llm, mode="off")
    result = wrapped("Hello world")
    assert result.startswith("response:")


@pytest.mark.asyncio
async def test_wrap_function_async():
    from asha.integrations.llm_wrap import wrap_function

    async def my_async_llm(prompt: str) -> str:
        return f"async-response:{prompt}"

    wrapped = wrap_function(my_async_llm, mode="off")
    result = await wrapped("Hello world")
    assert result.startswith("async-response:")


def test_wrap_function_fail_closed_on_process_error(monkeypatch):
    import asha.utils.dropin as dropin_mod
    from asha.exceptions import ASHAProcessingError
    import asha.integrations.llm_wrap as wrapper

    def boom(*args, **kwargs):
        raise RuntimeError("fail")

    monkeypatch.setattr(dropin_mod, "process", boom)

    def my_fn(prompt: str) -> str:
        return f"result:{prompt}"

    wrapped = wrapper.wrap_function(my_fn, mode="balanced")
    with pytest.raises(ASHAProcessingError):
        wrapped("hello")


# ---------------------------------------------------------------------------
# safe_wrap / auto_wrap
# ---------------------------------------------------------------------------


def test_safe_wrap_raises_on_incompatible_client():
    from asha.exceptions import ASHAWrapError
    from asha.integrations.llm_wrap import safe_wrap

    class _BadClient:
        pass  # no generate/create method

    with pytest.raises(ASHAWrapError):
        safe_wrap(_BadClient(), mode="balanced")


def test_auto_wrap_multiple_clients():
    from asha.integrations.llm_wrap import auto_wrap

    c1 = _SyncClient()
    c2 = _SyncClient()
    results = auto_wrap(c1, c2, mode="off")
    assert len(results) == 2


# ---------------------------------------------------------------------------
# UniversalWrapper
# ---------------------------------------------------------------------------


def test_universal_wrapper_wrap_client():
    from asha.integrations.llm_wrap import UniversalWrapper

    wrapper_obj = UniversalWrapper(mode="off")
    client = _SyncClient()
    wrapped = wrapper_obj.wrap_client(client)
    assert wrapped is client


def test_universal_wrapper_wrap_method():
    from asha.integrations.llm_wrap import UniversalWrapper

    wrapper_obj = UniversalWrapper(mode="off")
    client = _SyncClient()
    wrapped = wrapper_obj.wrap_method(client, "generate")
    assert wrapped is client
    result = client.generate(prompt="hello")
    assert isinstance(result, str)


def test_universal_wrapper_wrap_method_missing_raises():
    from asha.integrations.llm_wrap import UniversalWrapper

    wrapper_obj = UniversalWrapper(mode="off")
    client = _SyncClient()
    with pytest.raises(ValueError, match="not found on client"):
        wrapper_obj.wrap_method(client, "nonexistent_method")


def test_universal_wrapper_manual_wrap():
    from asha.integrations.llm_wrap import UniversalWrapper

    wrapper_obj = UniversalWrapper(mode="off", auto_detect=False)
    client = _SyncClient()
    wrapped = wrapper_obj.wrap_client(client)
    assert wrapped is client
