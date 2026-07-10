"""Shared ANCHOR guards for LLM responses (tool-call extraction)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .runtime import AnchorRuntime


def extract_tool_calls_from_response(response: Any) -> List[Dict[str, str]]:
    """Extract normalized tool calls from common LLM response shapes."""
    tool_calls: List[Dict[str, str]] = []

    choices = getattr(response, "choices", None)
    if choices:
        message = getattr(choices[0], "message", None)
        raw_calls = getattr(message, "tool_calls", None) or []
        for tool_call in raw_calls:
            function = getattr(tool_call, "function", None)
            if function is None:
                continue
            tool_calls.append(
                {
                    "name": str(getattr(function, "name", "") or ""),
                    "arguments": str(getattr(function, "arguments", "") or ""),
                }
            )
        return tool_calls

    content = getattr(response, "content", None)
    if isinstance(content, list):
        for block in content:
            if getattr(block, "type", "") == "tool_use":
                tool_calls.append(
                    {
                        "name": str(getattr(block, "name", "") or ""),
                        "arguments": json.dumps(getattr(block, "input", {}) or {}),
                    }
                )

    return tool_calls


def evaluate_llm_tool_calls(
    response: Any,
    runtime: AnchorRuntime,
    *,
    raise_on_block: bool = False,
    record: bool = True,
) -> None:
    """Validate tool calls proposed by an LLM response through ANCHOR."""
    for tool_call in extract_tool_calls_from_response(response):
        runtime.evaluate_action_request(
            "tool_call",
            {
                "tool_name": tool_call["name"],
                "arguments": tool_call["arguments"],
            },
            raise_on_block=raise_on_block,
            record=record,
        )
