"""
Optimization Stage - Stage 5 of the pipeline

MSDPC optimization for token reduction and prompt enhancement.
"""

from typing import Dict, Any
from ..components.stage_base import StageBase, StageResult, StageContext
from ...security.service import get_sanitized_content
from ..policy_gate import optimization_disabled


class OptimizationStage(StageBase):
    """
    MSDPC optimization stage for prompt optimization.

    This stage handles:
    - MSDPC (Multi-Stage Deterministic Prompt Compiler) integration
    - Token reduction (30-60%)
    - Quality scoring
    - Intent preservation
    - Performance metrics
    """

    def __init__(self):
        """Initialize optimization stage."""
        super().__init__("prompt_optimization")
        self.prompt_optimizer = None

    def _initialize_components(self, context: StageContext):
        """Initialize prompt optimizer component."""
        if self.prompt_optimizer is None:
            try:
                from ...compiler.optimizer_engine import PromptOptimizer

                self.prompt_optimizer = PromptOptimizer(use_msdpc=True)
            except ImportError as e:
                if context.debug_enabled:
                    print(
                        f"[Optimization] Failed to initialize PromptOptimizer: {e}")
                raise

    def execute(self, context: StageContext) -> StageResult:
        """
        Optimize compiled prompt using MSDPC.

        Args:
            context: Pipeline context with compiled prompt

        Returns:
            StageResult with optimized prompt and metrics
        """
        if optimization_disabled(context.config):
            source = context.compiled_prompt or context.original_content
            if context.config.get("privacy", True) and context.security_result:
                source = get_sanitized_content(
                    context.security_result, context.original_content
                )
            context.optimized_prompt = source
            return StageResult(
                success=True,
                data=source,
                metrics={
                    "token_reduction_percentage": 0.0,
                    "optimization_skipped": True,
                },
            )

        # Initialize components
        if self.prompt_optimizer is None:
            self._initialize_components(context)

        # Determine source content based on privacy setting
        if context.config.get("privacy", True) and context.security_result:
            source_content = get_sanitized_content(
                context.security_result, context.original_content
            )
        else:
            source_content = context.original_content

        # Use compiled prompt if available, otherwise use source content
        if context.compiled_prompt:
            source_content = context.compiled_prompt

        input_size = len(source_content)

        # Get optimization targets
        optimization_targets = context.config.get(
            "optimization_targets", ["tokens", "accuracy"]
        )

        # Determine format preservation
        preserve_format = context.config.get("preserve_format", True)

        from ...core.format_lock import FormatLock

        original_structure = FormatLock().detect_structure(context.original_content)
        if preserve_format and original_structure in ("json", "code"):
            locked_output = context.original_content
            context.optimized_prompt = locked_output
            return StageResult(
                success=True,
                data=locked_output,
                metrics={
                    "token_reduction_percentage": 0.0,
                    "format_lock_skipped": True,
                    "structure_type": original_structure,
                    "validation_passed": True,
                },
            )

        # Apply MSDPC optimization
        optimized_prompt, optimization_metrics = self.prompt_optimizer.optimize(
            source_content,
            context.ir,
            optimization_targets=optimization_targets,
            preserve_format=preserve_format,
        )

        # Validate optimization result
        validation_result = self._validate_optimization(
            optimized_prompt, optimization_metrics
        )

        # Add debug information
        self.add_debug_info(
            context,
            "MSDPC optimization completed",
            {
                "token_reduction": optimization_metrics.get(
                    "token_reduction_percentage", 0
                ),
                "msdpc_used": optimization_metrics.get("msdpc_used", False),
                "stages_applied": optimization_metrics.get("optimizations_applied", []),
                "validation_passed": validation_result["valid"],
            },
        )

        # Store result in context
        context.optimized_prompt = optimized_prompt

        # Calculate comprehensive metrics
        custom_metrics = {
            "token_reduction_percentage": optimization_metrics.get(
                "token_reduction_percentage", 0
            ),
            "original_tokens": optimization_metrics.get("original_tokens", 0),
            "optimized_tokens": optimization_metrics.get("optimized_tokens", 0),
            "msdpc_used": optimization_metrics.get("msdpc_used", False),
            "optimizations_applied": optimization_metrics.get(
                "optimizations_applied", []
            ),
            "validation_passed": validation_result["valid"],
            "validation_errors": len(validation_result.get("errors", [])),
        }

        # Add MSDPC-specific metrics if available
        msdpc_metrics = optimization_metrics.get("msdpc_metrics", {})
        if msdpc_metrics:
            custom_metrics.update(
                {
                    "clarity_score": msdpc_metrics.get("clarity_score", 0),
                    "structure_score": msdpc_metrics.get("structure_score", 0),
                    "efficiency_score": msdpc_metrics.get("efficiency_score", 0),
                    "intent_preserved": msdpc_metrics.get("intent_preserved", False),
                    "msdpc_processing_time_ms": msdpc_metrics.get(
                        "processing_time_ms", 0
                    ),
                }
            )

        # Add quality metrics
        quality_score = optimization_metrics.get("quality_score", 0)
        if quality_score:
            custom_metrics["quality_score"] = quality_score

        return StageResult(
            success=True if optimized_prompt and optimized_prompt.strip() else validation_result["valid"],
            data=optimized_prompt,
            metrics=custom_metrics,
        )

    def _validate_optimization(
        self, optimized_prompt: str, metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate optimization results."""
        errors = []
        warnings = []

        # Check for empty prompt
        if not optimized_prompt or not optimized_prompt.strip():
            errors.append("Optimized prompt is empty")

        # Check token reduction (expansion is a warning, not a hard failure)
        token_reduction = metrics.get("token_reduction_percentage", 0)
        if token_reduction < -50:
            warnings.append(f"Large token expansion: {token_reduction:.1f}%")
        elif token_reduction < 0:
            warnings.append("Token count increased during optimization")
        elif token_reduction == 0:
            warnings.append("No token reduction achieved")
        elif token_reduction > 80:
            warnings.append("Very high token reduction - may impact quality")

        # Check MSDPC usage
        if not metrics.get("msdpc_used", False):
            warnings.append("MSDPC was not used for optimization")

        # Check intent preservation
        msdpc_metrics = metrics.get("msdpc_metrics", {})
        if not msdpc_metrics.get("intent_preserved", True):
            warnings.append("Intent may not be preserved")

        # Check quality scores
        if msdpc_metrics:
            clarity = msdpc_metrics.get("clarity_score", 0)
            structure = msdpc_metrics.get("structure_score", 0)
            efficiency = msdpc_metrics.get("efficiency_score", 0)

            for score_name, score_value in [
                ("clarity", clarity),
                ("structure", structure),
                ("efficiency", efficiency),
            ]:
                if score_value < 0.3:
                    warnings.append(f"Low {score_name} score: {score_value}")
                elif score_value > 0.9:
                    warnings.append(
                        f"Very high {score_name} score: {score_value}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback optimization if MSDPC fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback optimization
        """
        # Use compiled prompt or original content as fallback
        if context.compiled_prompt:
            fallback_prompt = context.compiled_prompt
        elif context.config.get("privacy", True) and context.security_result:
            fallback_prompt = get_sanitized_content(
                context.security_result, context.original_content
            )
        else:
            fallback_prompt = context.original_content

        # Apply basic optimization
        optimized_prompt = self._basic_optimize(fallback_prompt)

        context.optimized_prompt = optimized_prompt

        self.add_debug_info(
            context,
            "Optimization fallback used",
            {
                "reason": "msdpc_optimization_failed",
                "fallback_type": "basic_optimization",
            },
        )

        # Calculate basic metrics
        original_length = len(fallback_prompt)
        optimized_length = len(optimized_prompt)
        reduction_percentage = (
            ((original_length - optimized_length) / original_length * 100)
            if original_length > 0
            else 0
        )

        return StageResult(
            success=True,
            data=optimized_prompt,
            metrics={
                "fallback_used": True,
                "token_reduction_percentage": reduction_percentage,
                "original_tokens": len(fallback_prompt.split()),
                "optimized_tokens": len(optimized_prompt.split()),
                "msdpc_used": False,
                "optimizations_applied": ["basic_cleanup"],
            },
        )

    def _basic_optimize(self, prompt: str) -> str:
        """Apply basic optimization without MSDPC."""
        # Remove extra whitespace
        import re

        optimized = re.sub(r"\s+", " ", prompt.strip())

        # Fix spacing around punctuation
        optimized = re.sub(r"\s+([.,!?;:])", r"\1", optimized)
        optimized = re.sub(r"([.,!?;:])\s+", r"\1 ", optimized)

        # Remove common filler words (basic)
        filler_words = ["very", "quite", "rather",
                        "somewhat", "really", "actually"]
        words = optimized.split()
        filtered_words = []

        for word in words:
            if word.lower().strip(".,!?;:") not in filler_words:
                filtered_words.append(word)

        optimized = " ".join(filtered_words)

        # Ensure proper capitalization and ending
        if optimized and optimized[0].islower():
            optimized = optimized[0].upper() + optimized[1:]

        if optimized and optimized[-1] not in ".!?":
            optimized += "."

        return optimized

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for optimization."""
        if not super().validate_input(context):
            return False

        # Check if we have content to optimize
        has_content = bool(
            context.compiled_prompt
            or (context.config.get("privacy", True) and context.security_result)
            or context.original_content
        )

        if not has_content:
            if context.debug_enabled:
                print("[Optimization] No content available for optimization")
            return False

        return True
