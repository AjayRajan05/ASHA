"""
Result Assembly Stage - Stage 7 of the pipeline

Compiles final result with comprehensive metrics and debugging information.
"""

from typing import Dict, Any, Optional, cast
from ..components.stage_base import StageBase, StageResult, StageContext
from ...security.service import get_sanitized_content


class ResultStage(StageBase):
    """
    Result assembly stage for final result compilation.

    This stage handles:
    - Result compilation
    - Metrics aggregation
    - Debug trace generation
    - Explainability data
    - Final validation
    """

    def __init__(self) -> None:
        """Initialize result assembly stage."""
        super().__init__("result_assembly")
        self.explainability_engine: Optional[Any] = None
        self.diff_engine: Optional[Any] = None

    def _initialize_components(self, context: StageContext) -> None:
        """Initialize explainability and diff engines."""
        if self.explainability_engine is None:
            try:
                from ...core.explainability import ExplainabilityEngine

                self.explainability_engine = ExplainabilityEngine()
            except ImportError:
                pass

        if self.diff_engine is None:
            try:
                from ...core.diff_engine import DiffEngine

                self.diff_engine = DiffEngine()
            except ImportError:
                pass

    def execute(self, context: StageContext) -> StageResult:
        """
        Assemble final result with all metrics and traces.

        Args:
            context: Pipeline context with all stage results

        Returns:
            StageResult with final assembled result
        """
        # Initialize components
        self._initialize_components(context)

        # Finalize context
        context.finalize()

        # Compile comprehensive result
        result = self._compile_result(context)

        # Validate final result
        validation_result = self._validate_final_result(result, context)

        # Add debug information
        self.add_debug_info(
            context,
            "Result assembly completed",
            {
                "result_success": result.get("success", False),
                "total_stages": len(context.stage_metrics),
                "successful_stages": len(context.get_successful_stages()),
                "validation_passed": validation_result["valid"],
            },
        )

        # Calculate metrics
        custom_metrics = {
            "total_stages": len(context.stage_metrics),
            "successful_stages": len(context.get_successful_stages()),
            "failed_stages": len(context.get_failed_stages()),
            "fallbacks_used": context.has_fallbacks(),
            "total_execution_time_ms": context.get_total_execution_time(),
            "validation_passed": validation_result["valid"],
            "validation_errors": len(validation_result.get("errors", [])),
        }

        return StageResult(
            success=validation_result["valid"], data=result, metrics=custom_metrics
        )

    def _compile_result(self, context: StageContext) -> Dict[str, Any]:
        """Compile comprehensive result from all stages."""
        result = {
            "success": True,
            "session_id": context.session_id,
            "prompts": self._compile_prompts(context),
            "security_result": self._compile_security_result(context),
            "routing_decision": self._compile_routing_decision(context),
            "optimization_metrics": self._compile_optimization_metrics(context),
            "response": context.model_response,
            "performance_metrics": self._compile_performance_metrics(context),
            "stage_metrics": context.stage_metrics,
            "processing_summary": context.get_processing_summary(),
        }

        # Add IR if available
        if context.ir:
            result["ir"] = (
                context.ir.to_dict()
                if hasattr(context.ir, "to_dict")
                else {"intent": "unknown"}
            )

        # Add explainability if available
        if self.explainability_engine:
            result["explainability"] = self._generate_explainability(context)

        # Add diff analysis if available
        if self.diff_engine and context.config.get("debug_diff", False):
            result["diff"] = self._generate_diff_analysis(context)

        # Add policy config
        result["policy_config"] = context.config.get("policy_config", {})

        # Check for any stage failures
        failed_stages = context.get_failed_stages()
        if failed_stages:
            if context.config.get("fallback_mode", True) and (
                context.optimized_prompt
                or context.compiled_prompt
                or context.security_result
            ):
                result["warnings"] = (
                    f"Stages with validation issues: {', '.join(failed_stages)}"
                )
            else:
                result["success"] = False
                result["error"] = (
                    f"Pipeline failed in stages: {', '.join(failed_stages)}"
                )

        return result

    def _compile_prompts(self, context: StageContext) -> Dict[str, str]:
        """Compile prompt information from all stages."""
        sanitized = context.original_content
        if context.security_result:
            sr = context.security_result
            if isinstance(sr, dict):
                sanitized = sr.get("sanitized_content", context.original_content)
            else:
                sanitized = getattr(sr, "sanitized_content", context.original_content)

        return {
            "original": context.original_content,
            "sanitized": sanitized,
            "compiled": context.compiled_prompt or "",
            "optimized": context.optimized_prompt or "",
        }

    def _compile_security_result(self, context: StageContext) -> Dict[str, Any]:
        """Compile security result information."""
        if not context.security_result:
            return {
                "is_safe": True,
                "detected_threats": [],
                "masked_entities": {},
                "sanitized_content": context.original_content,
                "threat_level": "LOW",
                "security_score": 0.0,
                "recommendations": [],
                "processing_time_ms": 0.0,
            }

        sr = context.security_result
        if isinstance(sr, dict):
            threat_level = sr.get("threat_level", "LOW")
            compiled = {
                "is_safe": sr.get("is_safe", True),
                "detected_threats": sr.get("detected_threats", []),
                "masked_entities": sr.get("masked_entities", {}) or {},
                "sanitized_content": sr.get(
                    "sanitized_content", context.original_content
                ),
                "threat_level": (
                    threat_level.value if hasattr(threat_level, "value") else threat_level
                ),
                "security_score": sr.get("security_score", 0.0),
                "recommendations": sr.get("recommendations", []),
                "processing_time_ms": sr.get("processing_time_ms", 0.0),
            }
            if sr.get("masking_map"):
                compiled["masking_map"] = sr["masking_map"]
            return compiled

        threat_level = getattr(sr, "threat_level", "LOW")
        compiled = {
            "is_safe": getattr(sr, "is_safe", True),
            "detected_threats": getattr(sr, "detected_threats", []),
            "masked_entities": getattr(sr, "masked_entities", {}) or {},
            "sanitized_content": getattr(
                sr, "sanitized_content", context.original_content
            ),
            "threat_level": (
                threat_level.value if hasattr(threat_level, "value") else threat_level
            ),
            "security_score": getattr(sr, "security_score", 0.0),
            "recommendations": getattr(sr, "recommendations", []),
            "processing_time_ms": getattr(sr, "processing_time_ms", 0.0),
        }
        masking_map = getattr(sr, "masking_map", None) or {}
        if masking_map:
            compiled["masking_map"] = masking_map
        return compiled

    def _compile_routing_decision(self, context: StageContext) -> Dict[str, Any]:
        """Compile routing decision information."""
        if not context.routing_decision:
            return {
                "selected_model": "default",
                "provider": "unknown",
                "confidence": 0.5,
                "reasoning": "fallback_routing",
                "estimated_cost": 0.0,
            }

        return {
            "selected_model": getattr(
                context.routing_decision.selected_model, "name", "default"
            ),
            "provider": getattr(
                context.routing_decision.selected_model, "provider", "unknown"
            ),
            "confidence": getattr(context.routing_decision, "confidence_score", 0.5),
            "reasoning": getattr(
                context.routing_decision, "reasoning", "fallback_routing"
            ),
            "estimated_cost": getattr(context.routing_decision, "estimated_cost", 0.0),
        }

    def _compile_optimization_metrics(self, context: StageContext) -> Dict[str, Any]:
        """Compile optimization metrics."""
        optimization_stage = context.get_stage_metrics("prompt_optimization")
        if not optimization_stage:
            return {"token_reduction_percentage": 0}

        return cast(
            Dict[str, Any],
            optimization_stage.get("metrics", {"token_reduction_percentage": 0}),
        )

    def _compile_performance_metrics(self, context: StageContext) -> Dict[str, Any]:
        """Compile performance metrics from all stages."""
        metrics = {}

        # Collect timing from each stage
        stage_times = {}
        total_time = 0

        for stage_name, stage_data in context.stage_metrics.items():
            if "execution_time_ms" in stage_data:
                stage_times[stage_name] = stage_data["execution_time_ms"]
                total_time += stage_data["execution_time_ms"]

        metrics.update(stage_times)
        metrics["total_pipeline_ms"] = total_time

        # Add stage-specific metrics
        if context.security_result:
            metrics["security_processing_ms"] = getattr(
                context.security_result, "processing_time_ms", 0
            )

        return metrics

    def _generate_explainability(self, context: StageContext) -> Dict[str, Any]:
        """Generate explainability data."""
        if self.explainability_engine is None:
            return {"error": "Explainability engine not available"}
        try:
            processing_result = {
                "success": True,
                "prompts": self._compile_prompts(context),
                "total_pipeline_ms": context.get_total_execution_time(),
            }

            explanation = self.explainability_engine.generate_explanation(
                session_id=context.session_id, processing_result=processing_result
            )

            return (
                explanation.__dict__
                if hasattr(explanation, "__dict__")
                else {
                    "summary": explanation.summary,
                    "confidence_score": explanation.confidence_score,
                    "human_readable_summary": explanation.human_readable_summary,
                }
            )
        except Exception as e:
            if context.debug_enabled:
                print(f"[Result] Failed to generate explainability: {e}")
            return {"error": "Explainability generation failed"}

    def _generate_diff_analysis(self, context: StageContext) -> Dict[str, Any]:
        """Generate diff analysis between original and optimized content."""
        if self.diff_engine is None:
            return {"error": "Diff engine not available"}
        try:
            original = context.original_content
            optimized = context.optimized_prompt or context.compiled_prompt or original

            diff_result = self.diff_engine.analyze_diff(
                original,
                optimized,
                context={
                    "session_id": context.session_id,
                    "security_level": context.config.get("security_level", "MEDIUM"),
                },
            )

            return {
                "diff": diff_result.to_dict(),
                "summary": self.diff_engine.format_diff(diff_result, "readable"),
            }
        except Exception as e:
            if context.debug_enabled:
                print(f"[Result] Failed to generate diff analysis: {e}")
            return {"error": "Diff analysis failed"}

    def _validate_final_result(
        self, result: Dict[str, Any], context: StageContext
    ) -> Dict[str, Any]:
        """Validate final assembled result."""
        errors = []
        warnings = []

        # Check required fields
        required_fields = ["success", "session_id", "prompts"]
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")

        # Check prompts structure
        if "prompts" in result:
            prompts = result["prompts"]
            required_prompts = ["original",
                                "sanitized", "compiled", "optimized"]
            for prompt_type in required_prompts:
                if prompt_type not in prompts:
                    warnings.append(f"Missing prompt type: {prompt_type}")

        # Check for consistent success flag
        if result.get("success", False) and context.get_failed_stages():
            warnings.append("Result marked as success but some stages failed")

        # Check performance metrics
        if "performance_metrics" in result:
            perf_metrics = result["performance_metrics"]
            if (
                "total_pipeline_ms" in perf_metrics
                and perf_metrics["total_pipeline_ms"] > 10000
            ):
                warnings.append("Pipeline took longer than 10 seconds")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback result assembly if main processing fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback result
        """
        # Create minimal fallback result
        fallback_result = {
            "success": False,
            "session_id": context.session_id,
            "error": "Result assembly failed - using fallback",
            "prompts": {
                "original": context.original_content,
                "sanitized": get_sanitized_content(
                    context.security_result, context.original_content
                )
                if context.security_result
                else context.original_content,
                "compiled": context.compiled_prompt or "",
                "optimized": context.optimized_prompt or "",
            },
            "stage_metrics": context.stage_metrics,
        }

        self.add_debug_info(
            context, "Result assembly fallback used", {
                "reason": "main_assembly_failed"}
        )

        return StageResult(
            success=True,
            data=fallback_result,
            metrics={
                "fallback_used": True,
                "total_stages": len(context.stage_metrics),
                "successful_stages": len(context.get_successful_stages()),
            },
        )

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for result assembly."""
        if not super().validate_input(context):
            return False

        # Check if context has any stage data
        if not context.stage_metrics:
            if context.debug_enabled:
                print("[Result] No stage metrics available for assembly")
            return False

        return True
