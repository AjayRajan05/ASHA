"""Shared tool-call bridging for all ANCHOR adapters."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional

from .runtime import AnchorRuntime


def tool_name_of(tool: Any) -> str:
    if isinstance(tool, str):
        return tool
    if hasattr(tool, "name") and getattr(tool, "name"):
        return str(getattr(tool, "name"))
    metadata = getattr(tool, "metadata", None)
    if metadata is not None and getattr(metadata, "name", None):
        return str(metadata.name)
    return getattr(tool, "__name__", type(tool).__name__)


def evaluate_tool_call(
    runtime: AnchorRuntime,
    tool_name: str,
    arguments: Any,
    *,
    record: bool = True,
) -> bool:
    return runtime.evaluate_action_request(
        "tool_call",
        {"tool_name": tool_name, "arguments": str(arguments)},
        raise_on_block=False,
        record=record,
    )


def block_message_for_tool(runtime: AnchorRuntime, tool_name: str) -> str:
    if runtime.state.approval_history:
        reason = runtime.state.approval_history[-1].verdict.reason
    else:
        reason = "Action blocked by mission contract."
    return f"Tool '{tool_name}' was denied: {reason}"


def guarded_tool_call(
    runtime: AnchorRuntime,
    tool_name: str,
    runner: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run a tool through ANCHOR action guard and optional sandbox."""
    payload = {"tool_name": tool_name, "arguments": str({"args": args, "kwargs": kwargs})}
    allowed = evaluate_tool_call(runtime, tool_name, payload["arguments"])
    if not allowed:
        return block_message_for_tool(runtime, tool_name)

    sandbox = getattr(runtime, "sandbox", None)
    if sandbox is not None:
        return sandbox.execute(runner, tool_name=tool_name, args=args, kwargs=kwargs)
    return runner(*args, **kwargs)


def _resolve_runner(tool: Any) -> Callable[..., Any]:
    if hasattr(tool, "_run"):
        def _run(*args: Any, **kwargs: Any) -> Any:
            result = tool._run(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return asyncio.run(result)
            return result
        return _run
    if hasattr(tool, "run"):
        def _run(*args: Any, **kwargs: Any) -> Any:
            result = tool.run(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return asyncio.run(result)
            return result
        return _run
    if hasattr(tool, "invoke"):
        def _invoke(*args: Any, **kwargs: Any) -> Any:
            if args and not kwargs:
                result = tool.invoke(args[0])
            else:
                result = tool.invoke(kwargs or {})
            if asyncio.iscoroutine(result):
                return asyncio.run(result)
            return result
        return _invoke
    if hasattr(tool, "fn") and callable(tool.fn):
        return tool.fn
    if hasattr(tool, "func") and callable(tool.func):
        return tool.func
    if callable(tool):
        return tool
    raise TypeError(f"Cannot wrap tool '{tool_name_of(tool)}' — no runnable entry point.")


class AnchoredToolDelegate:
    """
    Framework-agnostic governed tool wrapper.

    Preserves inner tool metadata and routes all execution paths through
    ANCHOR action guard + sandbox. Used by LangChain, LlamaIndex, AutoGen,
    MCP, and generic adapters.
    """

    def __init__(self, inner: Any, runtime: AnchorRuntime, *, name: Optional[str] = None) -> None:
        self._inner = inner
        self._runtime = runtime
        self._anchor_runtime = runtime
        self._anchor_wrapped = True
        self.name = name or tool_name_of(inner)
        self.description = getattr(inner, "description", "") or ""
        self.args_schema = getattr(inner, "args_schema", None)

    def _execute(self, *args: Any, **kwargs: Any) -> Any:
        runner = _resolve_runner(self._inner)
        return guarded_tool_call(self._runtime, self.name, runner, *args, **kwargs)

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return self._execute(*args, **kwargs)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        return self._execute(*args, **kwargs)

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:  # noqa: A002
        def runner() -> Any:
            if hasattr(self._inner, "invoke"):
                if config is not None:
                    return self._inner.invoke(input, config, **kwargs)
                return self._inner.invoke(input, **kwargs)
            if isinstance(input, dict):
                return self._inner.run(**input) if hasattr(self._inner, "run") else self._inner(**input)
            return self._inner.run(input, **kwargs) if hasattr(self._inner, "run") else self._inner(input)

        return guarded_tool_call(self._runtime, self.name, runner)

    async def ainvoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:  # noqa: A002
        return self.invoke(input, config=config, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._execute(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def wrap_tool(
    tool: Any,
    runtime: AnchorRuntime,
    *,
    name: Optional[str] = None,
) -> AnchoredToolDelegate:
    """Wrap any tool object with full ANCHOR governance."""
    if isinstance(tool, AnchoredToolDelegate):
        return tool
    if getattr(tool, "_anchor_wrapped", False):
        return tool  # type: ignore[return-value]
    return AnchoredToolDelegate(tool, runtime, name=name)


def wrap_callable_tool(
    tool: Any,
    runtime: AnchorRuntime,
    *,
    name: Optional[str] = None,
) -> AnchoredToolDelegate:
    """Backward-compatible alias for wrap_tool."""
    return wrap_tool(tool, runtime, name=name)
