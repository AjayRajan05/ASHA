"""Deep tool discovery for agent frameworks and graphs."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Set

from .base import tool_name


def discover_tools(target: Any, *, _seen: Optional[Set[int]] = None) -> List[Any]:
    """
    Recursively discover tools on agents, executors, graphs, and workflows.
    """
    if target is None:
        return []
    if _seen is None:
        _seen = set()

    oid = id(target)
    if oid in _seen:
        return []
    _seen.add(oid)

    found: List[Any] = []

    def _extend(items: Any) -> None:
        if not items:
            return
        if isinstance(items, dict):
            found.extend(items.values())
        elif isinstance(items, (list, tuple, set)):
            found.extend(items)
        else:
            found.append(items)

    for attr in (
        "tools",
        "tool",
        "tools_by_name",
        "function_map",
        "registered_tools",
    ):
        _extend(getattr(target, attr, None))

    get_tools = getattr(target, "get_tools", None)
    if callable(get_tools):
        try:
            _extend(get_tools())
        except Exception:
            pass

    for attr in ("agent", "bound", "agent_executor", "agent_worker", "executor"):
        child = getattr(target, attr, None)
        if child is not None:
            found.extend(discover_tools(child, _seen=_seen))

    # LangGraph / workflow nodes
    nodes = getattr(target, "nodes", None)
    if isinstance(nodes, dict):
        for node in nodes.values():
            found.extend(discover_tools(node, _seen=_seen))

    builder = getattr(target, "builder", None)
    if builder is not None:
        found.extend(discover_tools(builder, _seen=_seen))

    get_graph = getattr(target, "get_graph", None)
    if callable(get_graph):
        try:
            graph = get_graph()
            graph_nodes = getattr(graph, "nodes", None)
            if isinstance(graph_nodes, dict):
                for node in graph_nodes.values():
                    found.extend(discover_tools(node, _seen=_seen))
        except Exception:
            pass

    # AutoGen GroupChat agents
    agents = getattr(target, "agents", None)
    if isinstance(agents, (list, tuple)):
        for agent in agents:
            found.extend(discover_tools(agent, _seen=_seen))

    # LlamaIndex workflows
    for attr in ("workflow", "agent", "agents"):
        child = getattr(target, attr, None)
        if child is not None and not isinstance(child, (list, tuple, dict)):
            found.extend(discover_tools(child, _seen=_seen))

    # Deduplicate by tool name while preserving order
    unique: List[Any] = []
    names_seen: set[str] = set()
    for item in found:
        name = tool_name(item)
        if name in names_seen:
            continue
        names_seen.add(name)
        unique.append(item)
    return unique


def discover_tool_names(target: Any) -> List[str]:
    return [tool_name(t) for t in discover_tools(target)]
