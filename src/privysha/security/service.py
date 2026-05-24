"""
Canonical security execution path.

Used by SecurityStage, sanitize(), and privacy fallbacks so all security-only
processing shares one code path.
"""

from typing import Any, Dict, List, Optional, Union

from .security_layer import SecurityLayer, SecurityLevel, SecurityResult, ThreatType


def read_security_field(security_result: Any, field: str, default: Any = None) -> Any:
    """Read a field from SecurityResult dataclass or serialized dict."""
    if security_result is None:
        return default
    if isinstance(security_result, dict):
        return security_result.get(field, default)
    return getattr(security_result, field, default)


def get_sanitized_content(security_result: Any, fallback: str = "") -> str:
    """Return sanitized text from any security result representation."""
    content = read_security_field(security_result, "sanitized_content", fallback)
    return content if content is not None else fallback


def normalize_security_level(
    level: Union[str, SecurityLevel],
    *,
    default: SecurityLevel = SecurityLevel.MEDIUM,
) -> SecurityLevel:
    """Convert config string or enum to SecurityLevel."""
    if isinstance(level, SecurityLevel):
        return level
    if isinstance(level, str):
        try:
            return SecurityLevel[level.upper()]
        except KeyError:
            return default
    return default


def _apply_safety_classifier(
    content: str,
    *,
    threat_blocking: bool,
) -> Optional[Any]:
    import os

    if os.environ.get("PRIVYSHA_DISABLE_ML", "").lower() in ("1", "true", "yes"):
        return None
    try:
        from ..core.safety_classifier import SafetyClassifier

        classifier = SafetyClassifier()
        return classifier.classify_safety(content)
    except ImportError:
        return None
    except Exception:
        return None


def _build_hybrid_masked_entities(pii_entities) -> Dict[str, Any]:
    """Normalize hybrid PII entities to masked_entities dict format."""
    masked_entities: Dict[str, Any] = {}
    for i, entity in enumerate(pii_entities):
        entity_type = getattr(entity, "entity_type", None) or getattr(
            entity, "pii_type", "unknown"
        )
        masked_entities[f"entity_{i}"] = {
            "type": entity_type,
            "original_length": len(getattr(entity, "text", "")),
            "severity": getattr(entity, "confidence", 0.8),
        }
    return masked_entities


def _merge_with_safety(
    base: SecurityResult,
    safety_result: Optional[Any],
    *,
    hybrid_pii_used: bool = False,
) -> SecurityResult:
    """Overlay safety classifier metadata onto a SecurityResult."""
    if not safety_result:
        return SecurityResult(
            is_safe=base.is_safe,
            threat_level=base.threat_level,
            detected_threats=base.detected_threats,
            sanitized_content=base.sanitized_content,
            masked_entities=base.masked_entities,
            security_score=base.security_score,
            recommendations=base.recommendations,
            processing_time_ms=base.processing_time_ms,
            hybrid_pii_used=hybrid_pii_used,
            safety_classifier_used=False,
            masking_map=getattr(base, "masking_map", {}) or {},
        )

    extra_threats: List[ThreatType] = list(base.detected_threats)
    safety_threats = getattr(safety_result, "threats", None) or []
    for threat in safety_threats:
        if threat not in extra_threats:
            extra_threats.append(threat)

    threat_level = base.threat_level
    safety_level = getattr(safety_result, "safety_level", None)
    if safety_level is not None and not getattr(safety_result, "is_safe", True):
        try:
            threat_level = SecurityLevel[safety_level.name.upper()]
        except (AttributeError, KeyError):
            pass

        return SecurityResult(
            is_safe=getattr(safety_result, "is_safe", base.is_safe),
            threat_level=threat_level,
            detected_threats=extra_threats,
            sanitized_content=base.sanitized_content,
            masked_entities=base.masked_entities,
            security_score=getattr(safety_result, "confidence_score", base.security_score),
            recommendations=getattr(safety_result, "recommendations", base.recommendations)
            or base.recommendations,
            processing_time_ms=base.processing_time_ms,
            hybrid_pii_used=hybrid_pii_used,
            safety_classifier_used=True,
            masking_map=getattr(base, "masking_map", {}) or {},
        )


def run_security(
    content: str,
    config: Optional[Dict[str, Any]] = None,
) -> SecurityResult:
    """
    Run the canonical security-only path (PII masking + threat analysis).

    Args:
        content: Text to secure.
        config: Optional settings:
            - security_level: str or SecurityLevel (default MEDIUM)
            - pii_mode: "rule" | "hybrid" | "ml_only" (default "rule")
            - threat_blocking: block unsafe content (default True)
            - debug_enabled: enable hybrid detector debug (default False)

    Returns:
        SecurityResult dataclass.
    """
    config = config or {}
    enable_pii = config.get("enable_pii_detection", True)
    enable_injection = config.get("enable_injection_detection", True)
    pii_masking = config.get("pii_masking", config.get("privacy", True))
    if not pii_masking:
        enable_pii = False

    if not enable_pii and not enable_injection:
        return SecurityResult(
            is_safe=True,
            threat_level=SecurityLevel.LOW,
            detected_threats=[],
            sanitized_content=content,
            masked_entities={},
            security_score=0.0,
            recommendations=[],
            processing_time_ms=0.0,
        )

    security_level = normalize_security_level(
        config.get("security_level", SecurityLevel.MEDIUM)
    )
    pii_mode = config.get("pii_mode", "rule")
    threat_blocking = config.get("threat_blocking", True)
    debug_enabled = config.get("debug_enabled", False)

    if not enable_pii:
        pii_mode = "rule"

    layer = SecurityLayer(
        security_level,
        reversible_masking=bool(config.get("reversible", False)),
    )
    hybrid_detector = None

    if enable_pii and pii_mode != "rule":
        try:
            from ..core.hybrid_pii import HybridPIIDetector

            hybrid_detector = HybridPIIDetector(debug_enabled=debug_enabled)
        except ImportError:
            hybrid_detector = None

    if hybrid_detector:
        pii_result = hybrid_detector.detect(content)
        masked_content = pii_result.masked_text
        masked_entities = _build_hybrid_masked_entities(pii_result.entities)
        base = SecurityResult(
            is_safe=True,
            threat_level=SecurityLevel.LOW,
            detected_threats=[],
            sanitized_content=masked_content,
            masked_entities=masked_entities,
            security_score=0.0,
            recommendations=[],
            processing_time_ms=0.0,
            hybrid_pii_used=True,
            safety_classifier_used=False,
            masking_map={},
        )
    else:
        base = layer.process(content, mask_pii=enable_pii)

    if enable_injection:
        safety_result = _apply_safety_classifier(
            base.sanitized_content, threat_blocking=threat_blocking
        )
    else:
        safety_result = None
    if safety_result and not getattr(safety_result, "is_safe", True) and threat_blocking:
        level = getattr(safety_result, "safety_level", None)
        level_name = getattr(level, "value", "unsafe")
        raise ValueError(f"Content blocked by safety classifier: {level_name}")

    return _merge_with_safety(
        base,
        safety_result,
        hybrid_pii_used=hybrid_detector is not None,
    )


def run_security_only(
    content: str,
    *,
    security_level: Union[str, SecurityLevel] = SecurityLevel.HIGH,
    pii_mode: str = "rule",
    threat_blocking: bool = True,
    debug_enabled: bool = False,
    reversible: bool = False,
) -> SecurityResult:
    """Convenience wrapper for security-only public APIs (e.g. sanitize())."""
    return run_security(
        content,
        {
            "security_level": security_level,
            "pii_mode": pii_mode,
            "threat_blocking": threat_blocking,
            "debug_enabled": debug_enabled,
            "reversible": reversible,
        },
    )
