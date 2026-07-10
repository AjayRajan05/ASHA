"""Universal ANCHOR adapter entrypoint and framework registry."""

from __future__ import annotations

from typing import Any, Optional

from ..runtime import AnchorRuntime
from .crewai import anchor_crewai
from .generic import anchor_generic


def anchor_any(
    target: Any,
    *,
    risk_tolerance: str = "LOW",
    warn_policy: Optional[str] = None,
    interactive: Optional[bool] = None,
    isolation: str = "auto",
) -> Any:
    """
    One-line ANCHOR adoption for any supported agentic framework.

    Dispatches to the best adapter based on target type and capabilities.
    """
    runtime = AnchorRuntime(
        risk_tolerance=risk_tolerance,
        warn_policy=warn_policy,
        interactive=interactive,
        isolation=isolation,
    )

    try:
        from .asha_agent import anchor_asha_agent, is_asha_agent

        if is_asha_agent(target):
            return anchor_asha_agent(
                target,
                runtime=runtime,
                isolation=isolation,
            )
    except ImportError:
        pass

    if _is_crewai(target):
        return anchor_crewai(
            target,
            risk_tolerance=risk_tolerance,
            warn_policy=warn_policy,
            interactive=interactive,
            isolation=isolation,
        )

    try:
        from .graph import anchor_graph, is_agent_graph

        if is_agent_graph(target):
            return anchor_graph(target, runtime=runtime, isolation=isolation)
    except ImportError:
        pass

    try:
        from .mcp import anchor_mcp, is_mcp_server

        if is_mcp_server(target):
            return anchor_mcp(target, runtime=runtime, isolation=isolation)
    except ImportError:
        pass

    try:
        from .langchain import anchor_langchain, is_langchain_agent

        if is_langchain_agent(target):
            return anchor_langchain(target, runtime=runtime, isolation=isolation)
    except ImportError:
        pass

    try:
        from .autogen import anchor_autogen, is_autogen_agent

        if is_autogen_agent(target):
            return anchor_autogen(target, runtime=runtime, isolation=isolation)
    except ImportError:
        pass

    try:
        from .llamaindex import anchor_llamaindex, is_llamaindex_agent

        if is_llamaindex_agent(target):
            return anchor_llamaindex(target, runtime=runtime, isolation=isolation)
    except ImportError:
        pass

    return anchor_generic(
        target,
        runtime=runtime,
        isolation=isolation,
        risk_tolerance=risk_tolerance,
        warn_policy=warn_policy,
        interactive=interactive,
    )


def _is_crewai(target: Any) -> bool:
    module = type(target).__module__ or ""
    if "crewai" in module:
        return True
    return (
        callable(getattr(target, "kickoff", None))
        and hasattr(target, "agents")
        and hasattr(target, "tasks")
    )
