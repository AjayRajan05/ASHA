# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unified wrapper for PrivySHA with async and streaming support.

Provides drop-in wrapping for any LLM client with fail-safe execution.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Optional
from functools import wraps

from ..core.streaming import (
    extract_prompt_from_kwargs,
    replace_prompt_in_kwargs,
    handle_streaming_response,
    handle_async_streaming_response,
    is_streaming_response,
)
from ..core.output_guard import OutputGuard


def _process_prompt_for_wrap(
    prompt: str,
    mode: str,
    *,
    privacy: bool = True,
    token_budget: int = 1200,
) -> str:
    """Run process() and return a prompt string for wrapped clients."""
    from .dropin import process, _coerce_process_output

    if not privacy:
        processed = process(
            prompt, privacy=False, token_budget=token_budget, mode="off"
        )
        return _coerce_process_output(processed, prompt)

    if mode == "strict":
        processed = process(
            prompt,
            privacy=True,
            token_budget=min(token_budget, 800),
            security_level="high",
            mode="strict",
        )
    elif mode == "balanced":
        processed = process(
            prompt,
            privacy=True,
            token_budget=token_budget,
            security_level="medium",
            mode="balanced",
        )
    elif mode == "lite":
        processed = process(
            prompt,
            privacy=True,
            token_budget=max(token_budget, 2000),
            security_level="low",
            mode="lite",
        )
    else:
        processed = process(
            prompt,
            privacy=False,
            token_budget=token_budget,
            mode="off",
        )
    return _coerce_process_output(processed, prompt)


def _guard_response(output_guard: OutputGuard, response: Any, kwargs: dict[str, Any]) -> Any:
    """Validate LLM response with optional format constraint."""
    response_format = kwargs.get("response_format")
    fmt: Optional[str] = (
        response_format if isinstance(response_format, str) else None
    )
    return output_guard.guard_output(response, fmt)


def _wrap_nested_chat_completions(
    client: Any,
    mode: str,
    *,
    privacy: bool = True,
    token_budget: int = 1200,
) -> bool:
    """
    Wrap OpenAI-style client.chat.completions.create if present.

    Returns True if nested wrapping was applied.
    """
    chat = getattr(client, "chat", None)
    if chat is None:
        return False
    completions = getattr(chat, "completions", None)
    if completions is None:
        return False
    original_create = getattr(completions, "create", None)
    if not callable(original_create):
        return False

    def wrapped_create(*args: Any, **kwargs: Any) -> Any:
        try:
            prompt = extract_prompt_from_kwargs(kwargs)
            if prompt:
                kwargs = replace_prompt_in_kwargs(
                    kwargs,
                    _process_prompt_for_wrap(
                        prompt, mode, privacy=privacy, token_budget=token_budget
                    ),
                )
            response = original_create(*args, **kwargs)
            if kwargs.get("stream", False) and is_streaming_response(response):
                return handle_streaming_response(response)
            output_guard = OutputGuard()
            return _guard_response(output_guard, response, kwargs)
        except Exception:
            return original_create(*args, **kwargs)

    completions.create = wrapped_create
    return True


def wrap_llm(
    client: Any,
    mode: str = "balanced",
    *,
    privacy: bool = True,
    token_budget: int = 1200,
) -> Any:
    """
    Wrap any LLM client with PrivySHA security and optimization.

    Works with both sync and async clients, handles streaming automatically.

    Args:
        client: LLM client to wrap (OpenAI, Anthropic, etc.)
        mode: Processing mode ("balanced", "strict", "lite", "auto")

    Returns:
        Wrapped client with PrivySHA protection
    """
    # OpenAI-style nested clients (e.g. MockLLM, OpenAI SDK)
    if _wrap_nested_chat_completions(
        client, mode, privacy=privacy, token_budget=token_budget
    ):
        return client

    # Find the main generation method
    generation_method = _find_generation_method(client)

    if not generation_method:
        raise ValueError(
            "Could not find compatible generation method on client. "
            "Supported clients: OpenAI, Anthropic, Gemini, HuggingFace, Ollama. "
            "Make sure your client has a generate/create method."
        )

    original_method = getattr(client, generation_method)

    # Check if method is async
    if inspect.iscoroutinefunction(original_method):
        # Wrap async method
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Extract and process prompt
                prompt = extract_prompt_from_kwargs(kwargs)

                if prompt:
                    optimized_prompt = _process_prompt_for_wrap(
                        prompt,
                        mode,
                        privacy=privacy,
                        token_budget=token_budget,
                    )
                    kwargs = replace_prompt_in_kwargs(kwargs, optimized_prompt)

                # Call original method
                response = await original_method(*args, **kwargs)

                # Handle streaming
                if kwargs.get("stream", False) and is_streaming_response(response):
                    return handle_async_streaming_response(response)

                # Validate output
                output_guard = OutputGuard()
                return _guard_response(output_guard, response, kwargs)

            except Exception:
                # 🔥 FAIL SAFE - return original behavior
                return await original_method(*args, **kwargs)

        setattr(client, generation_method, async_wrapper)

    else:
        # Wrap sync method
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Extract and process prompt
                prompt = extract_prompt_from_kwargs(kwargs)

                if prompt:
                    optimized_prompt = _process_prompt_for_wrap(
                        prompt,
                        mode,
                        privacy=privacy,
                        token_budget=token_budget,
                    )
                    kwargs = replace_prompt_in_kwargs(kwargs, optimized_prompt)

                # Call original method
                response = original_method(*args, **kwargs)

                # Handle streaming
                if kwargs.get("stream", False) and is_streaming_response(response):
                    return handle_streaming_response(response)

                # Validate output
                output_guard = OutputGuard()
                return _guard_response(output_guard, response, kwargs)

            except Exception:
                # 🔥 FAIL SAFE - return original behavior
                return original_method(*args, **kwargs)

        setattr(client, generation_method, sync_wrapper)

    return client


def wrap_function(func: Callable[..., Any], mode: str = "balanced") -> Callable[..., Any]:
    """
    Wrap a function that takes a prompt as first argument.

    Args:
        func: Function to wrap
        mode: Processing mode

    Returns:
        Wrapped function with PrivySHA protection
    """
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                if args:
                    # Process first positional argument (prompt)
                    prompt = str(args[0])
                    from .dropin import process, _coerce_process_output

                    processed = process(prompt, mode=mode)
                    optimized_prompt = _coerce_process_output(processed, prompt)
                    new_args = (optimized_prompt,) + args[1:]
                    return await func(*new_args, **kwargs)

                return await func(*args, **kwargs)

            except Exception:
                # Fail-safe
                return await func(*args, **kwargs)

        return async_wrapper

    else:

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                if args:
                    # Process first positional argument (prompt)
                    prompt = str(args[0])
                    from .dropin import process, _coerce_process_output

                    processed = process(prompt, mode=mode)
                    optimized_prompt = _coerce_process_output(processed, prompt)
                    new_args = (optimized_prompt,) + args[1:]
                    return func(*new_args, **kwargs)

                return func(*args, **kwargs)

            except Exception:
                # Fail-safe
                return func(*args, **kwargs)

        return sync_wrapper


def _find_generation_method(client: Any) -> Optional[str]:
    """
    Find the main generation method on an LLM client.

    Args:
        client: LLM client instance (OpenAI, Anthropic, Gemini, etc.)

    Returns:
        Method name string if found, None otherwise

    Supported clients:
        - OpenAI: 'create', 'generate', 'chat.completions.create'
        - Anthropic: 'messages.create', 'complete'
        - Gemini: 'generate_content', 'send_message'
        - HuggingFace: 'generate', '__call__'
        - Ollama: 'generate', 'chat'
    """
    # Common method names across different SDKs
    method_names = [
        "create",  # OpenAI
        "generate",  # Anthropic, HuggingFace
        "chat",  # Some custom clients
        "completion",  # Some older clients
        "predict",  # Some ML clients
        "run",  # Generic
    ]

    for method_name in method_names:
        if hasattr(client, method_name):
            method = getattr(client, method_name)
            if callable(method):
                return method_name

    return None


class UniversalWrapper:
    """
    Universal wrapper that can adapt to any LLM interface.

    Provides automatic method detection and wrapping with fail-safe execution.
    """

    def __init__(self, mode: str = "balanced", auto_detect: bool = True) -> None:
        """
        Initialize universal wrapper.

        Args:
            mode: Processing mode
            auto_detect: Whether to auto-detect generation methods
        """
        self.mode = mode
        self.auto_detect = auto_detect
        self.output_guard = OutputGuard()

    def wrap_client(self, client: Any) -> Any:
        """
        Wrap an entire LLM client.

        Args:
            client: LLM client to wrap

        Returns:
            Wrapped client
        """
        if self.auto_detect:
            return wrap_llm(client, self.mode)
        else:
            # Manual wrapping for specific methods
            return self._manual_wrap(client)

    def wrap_method(self, client: Any, method_name: str) -> Any:
        """
        Wrap a specific method on a client.

        Args:
            client: LLM client
            method_name: Name of method to wrap

        Returns:
            Client with wrapped method
        """
        if not hasattr(client, method_name):
            raise ValueError(
                f"Method '{method_name}' not found on client. "
                "Available methods depend on client type."
            )

        original_method = getattr(client, method_name)

        if inspect.iscoroutinefunction(original_method):

            async def async_method_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    # Process prompt if present
                    prompt = extract_prompt_from_kwargs(kwargs)
                    if prompt:
                        from .dropin import process, _coerce_process_output

                        processed = process(prompt, mode=self.mode)
                        optimized_prompt = _coerce_process_output(processed, prompt)
                        kwargs = replace_prompt_in_kwargs(
                            kwargs, optimized_prompt
                        )

                    # Call original method
                    response = await original_method(*args, **kwargs)

                    # Handle streaming and validation
                    if kwargs.get("stream", False) and is_streaming_response(response):
                        return handle_async_streaming_response(response)

                    return _guard_response(self.output_guard, response, kwargs)

                except Exception:
                    return await original_method(*args, **kwargs)

            setattr(client, method_name, async_method_wrapper)

        else:

            def sync_method_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    # Process prompt if present
                    prompt = extract_prompt_from_kwargs(kwargs)
                    if prompt:
                        from .dropin import process, _coerce_process_output

                        processed = process(prompt, mode=self.mode)
                        optimized_prompt = _coerce_process_output(processed, prompt)
                        kwargs = replace_prompt_in_kwargs(
                            kwargs, optimized_prompt
                        )

                    # Call original method
                    response = original_method(*args, **kwargs)

                    # Handle streaming and validation
                    if kwargs.get("stream", False) and is_streaming_response(response):
                        return handle_streaming_response(response)

                    return _guard_response(self.output_guard, response, kwargs)

                except Exception:
                    return original_method(*args, **kwargs)

            setattr(client, method_name, sync_method_wrapper)

        return client

    def _manual_wrap(self, client: Any) -> Any:
        """
        Manual wrapping when auto-detect is disabled.

        Args:
            client: LLM client to wrap

        Returns:
            Wrapped client
        """
        # Try common methods manually
        methods_to_try = ["create", "generate", "chat"]

        for method_name in methods_to_try:
            if hasattr(client, method_name):
                return self.wrap_method(client, method_name)

        raise ValueError("No compatible generation method found")


# Convenience functions for quick wrapping
def safe_wrap(client: Any, mode: str = "balanced") -> Any:
    """
    Quick safe wrapper with maximum compatibility.

    Args:
        client: LLM client to wrap
        mode: Processing mode

    Returns:
        Safely wrapped client
    """
    try:
        return wrap_llm(client, mode)
    except Exception:
        # Return original client if wrapping fails
        return client


def auto_wrap(*clients: Any, mode: str = "balanced") -> list[Any]:
    """
    Wrap multiple clients automatically.

    Args:
        *clients: LLM clients to wrap
        mode: Processing mode

    Returns:
        List of wrapped clients
    """
    wrapped_clients = []
    for client in clients:
        try:
            wrapped = wrap_llm(client, mode)
            wrapped_clients.append(wrapped)
        except Exception:
            # Keep original client if wrapping fails
            wrapped_clients.append(client)

    return wrapped_clients
