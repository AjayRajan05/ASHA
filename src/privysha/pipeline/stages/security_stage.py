"""
Security Processing Stage - Stage 1 of the pipeline

Handles PII detection, threat analysis, and content sanitization.
"""

from ..components.stage_base import StageBase, StageResult, StageContext
from ...security.service import run_security
from ...security.security_layer import SecurityResult, SecurityLevel
from ..policy_gate import security_disabled


class SecurityStage(StageBase):
    """
    Security processing stage for PII detection and threat analysis.

    Delegates to security.service.run_security — the canonical security path.
    """

    def __init__(self):
        """Initialize security stage."""
        super().__init__("security_processing")
        self.enhanced_risk_analyzer = None

    def _initialize_components(self, context: StageContext):
        """Initialize optional risk analyzer."""
        try:
            from ...core.risk_analyzer import EnhancedRiskAnalyzer

            self.enhanced_risk_analyzer = EnhancedRiskAnalyzer()
        except ImportError as e:
            if context.debug_enabled:
                print(f"[Security] Risk analyzer unavailable: {e}")

    def execute(self, context: StageContext) -> StageResult:
        """Execute security processing on input content."""
        if self.enhanced_risk_analyzer is None:
            self._initialize_components(context)

        content = context.original_content

        if security_disabled(context.config):
            security_result = SecurityResult(
                is_safe=True,
                threat_level=SecurityLevel.LOW,
                detected_threats=[],
                sanitized_content=content,
                masked_entities={},
                security_score=0.0,
                recommendations=[],
                processing_time_ms=0.0,
            )
            context.security_result = security_result
            return StageResult(
                success=True,
                data=security_result,
                metrics={"security_skipped": True},
            )

        risk_assessment = None
        if self.enhanced_risk_analyzer:
            risk_assessment = self.enhanced_risk_analyzer.analyze(content)

        security_result = run_security(content, context.config)

        self.add_debug_info(
            context,
            "Security processing completed",
            {
                "threats_detected": len(security_result.detected_threats),
                "pii_masked": len(security_result.masked_entities),
                "is_safe": security_result.is_safe,
                "pii_pipeline_used": security_result.hybrid_pii_used,
                "pii_mode": context.config.get("pii_mode", "rule"),
            },
        )

        context.security_result = security_result

        custom_metrics = {
            "threats_detected": len(security_result.detected_threats),
            "pii_entities_masked": len(security_result.masked_entities),
            "security_score": security_result.security_score,
            "threat_level": (
                security_result.threat_level.value
                if hasattr(security_result.threat_level, "value")
                else security_result.threat_level
            ),
            "hybrid_pii_used": security_result.hybrid_pii_used,
            "safety_classifier_used": security_result.safety_classifier_used,
            "multi_stage_pii_used": security_result.hybrid_pii_used,
        }

        if risk_assessment:
            custom_metrics.update(
                {
                    "risk_score": getattr(risk_assessment, "score", 0.0),
                    "recommended_mode": getattr(
                        risk_assessment, "recommended_mode", "BALANCED"
                    ),
                }
            )

        return StageResult(success=True, data=security_result, metrics=custom_metrics)

    def fallback(self, context: StageContext) -> StageResult:
        """Fallback security processing via canonical service."""
        content = context.original_content

        try:
            fallback_config = dict(context.config)
            fallback_config["pii_mode"] = "rule"
            security_result = run_security(content, fallback_config)
        except Exception:
            from ...utils.dropin_privacy import SECURITY_FAIL_CLOSED_PLACEHOLDER

            if context.config.get("security_fail_closed"):
                sanitized = SECURITY_FAIL_CLOSED_PLACEHOLDER
            else:
                sanitized = content
            security_result = SecurityResult(
                is_safe=True,
                threat_level=SecurityLevel.LOW,
                detected_threats=[],
                sanitized_content=sanitized,
                masked_entities={},
                security_score=0.0,
                recommendations=[],
                processing_time_ms=0.0,
            )

        context.security_result = security_result

        return StageResult(
            success=True,
            data=security_result,
            metrics={"fallback_used": True},
        )

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for security processing."""
        if not super().validate_input(context):
            return False

        content = context.original_content
        if not content or not content.strip():
            return False
        if len(content) > 100000:
            return False

        return True
