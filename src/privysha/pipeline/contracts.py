"""
Shared pipeline contracts — types and interfaces with no implementation deps.

Import from here when a module only needs type contracts, not orchestration logic.
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable

from .components.stage_context import StageContext, create_context
from .components.stage_base import StageResult, StageBase
from ..security.security_layer import SecurityResult, SecurityLevel, ThreatType
from ..security.service import read_security_field, get_sanitized_content


@runtime_checkable
class SecurityResultLike(Protocol):
    """Minimal security result interface for cross-layer typing."""

    is_safe: bool
    sanitized_content: str
    masked_entities: Dict[str, Any]
    detected_threats: Any
    threat_level: Any
    security_score: float
    recommendations: Any
    processing_time_ms: float


__all__ = [
    "StageContext",
    "StageResult",
    "StageBase",
    "create_context",
    "SecurityResult",
    "SecurityLevel",
    "ThreatType",
    "SecurityResultLike",
    "read_security_field",
    "get_sanitized_content",
]
