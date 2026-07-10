"""Framework adapters for ANCHOR mission governance."""

__all__: list[str] = []

try:
    from .crewai import AnchoredTool, anchor_crewai

    __all__.extend(["anchor_crewai", "AnchoredTool"])
except ImportError:
    anchor_crewai = None  # type: ignore[misc, assignment]
    AnchoredTool = None  # type: ignore[misc, assignment]

from .generic import anchor_generic
from .registry import anchor_any

__all__.extend(["anchor_any", "anchor_generic"])

try:
    from .asha_agent import anchor_asha_agent

    __all__.append("anchor_asha_agent")
except ImportError:
    anchor_asha_agent = None  # type: ignore[misc, assignment]

try:
    from .graph import anchor_graph

    __all__.append("anchor_graph")
except ImportError:
    anchor_graph = None  # type: ignore[misc, assignment]

try:
    from .langchain import anchor_langchain

    __all__.append("anchor_langchain")
except ImportError:
    anchor_langchain = None  # type: ignore[misc, assignment]

try:
    from .mcp import anchor_mcp

    __all__.append("anchor_mcp")
except ImportError:
    anchor_mcp = None  # type: ignore[misc, assignment]

try:
    from .autogen import anchor_autogen

    __all__.append("anchor_autogen")
except ImportError:
    anchor_autogen = None  # type: ignore[misc, assignment]

try:
    from .llamaindex import anchor_llamaindex

    __all__.append("anchor_llamaindex")
except ImportError:
    anchor_llamaindex = None  # type: ignore[misc, assignment]
