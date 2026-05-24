"""
Base class for all pipeline stages
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

from .stage_context import StageContext
from ...security.service import get_sanitized_content


@dataclass
class StageResult:
    """Result of a pipeline stage execution."""

    success: bool
    data: Any
    metrics: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class StageBase(ABC):
    """
    Base class for all pipeline stages.

    Provides common functionality for error handling, metrics,
    and fallback processing.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize stage.

        Args:
            name: Stage name for logging and metrics
        """
        self.name = name

    @abstractmethod
    def execute(self, context: StageContext) -> StageResult:
        """
        Execute the stage logic.

        Args:
            context: Pipeline context with data and configuration

        Returns:
            StageResult with execution results
        """

    @abstractmethod
    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback execution if main execution fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback results
        """

    def process(self, context: StageContext) -> StageResult:
        """
        Main processing method with error handling and observability.

        Args:
            context: Pipeline context

        Returns:
            StageResult with execution results
        """
        start_time = time.time()

        # Get input text for tracing
        input_text = self._get_input_text(context)

        # Log stage start if trace context is available
        trace_ctx = getattr(context, "trace_context", None)
        if trace_ctx:
            trace_ctx.log_stage_start(self.name, input_text)

        from ...integrations.otel import stage_span

        with stage_span(self.name):
            try:
                # Execute main stage logic
                result = self.execute(context)
                result.execution_time_ms = (time.time() - start_time) * 1000

                # Get output text and changes for tracing
                output_text = self._get_output_text(context, result)
                changes = self._extract_changes(context, result)
                metrics = result.metrics

                # Log stage completion if trace context is available
                if trace_ctx:
                    trace_ctx.log_stage_end(
                        stage_name=self.name,
                        output_text=output_text,
                        changes=changes,
                        metrics=metrics,
                    )

                # Add stage metrics to context
                context.stage_metrics[self.name] = {
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms,
                    "metrics": result.metrics,
                    "data": result.data,
                }

                return result

            except Exception as e:
                trace_ctx = getattr(context, "trace_context", None)
                # Log error and try fallback
                if trace_ctx:
                    trace_ctx.log_error(
                        stage=self.name,
                        error_type=type(e).__name__,
                        message=str(e),
                        fallback="attempting_fallback",
                        impact="stage_execution_failed",
                    )
                elif context.debug_enabled:
                    print(f"[{self.name}] Stage failed: {str(e)}")

                try:
                    fallback_result = self.fallback(context)
                    fallback_result.execution_time_ms = (
                        time.time() - start_time
                    ) * 1000

                    # Get fallback output and changes for tracing
                    output_text = self._get_output_text(context, fallback_result)
                    changes = self._extract_changes(context, fallback_result)

                    # Log fallback completion if trace context is available
                    if trace_ctx:
                        trace_ctx.log_stage_end(
                            stage_name=self.name,
                            output_text=output_text,
                            changes=changes,
                            metrics=fallback_result.metrics,
                            error={
                                "type": type(e).__name__,
                                "message": str(e),
                                "fallback": "used",
                                "impact": "reduced_functionality",
                            },
                        )

                    # Update context with fallback metrics
                    context.stage_metrics[self.name] = {
                        "success": fallback_result.success,
                        "execution_time_ms": fallback_result.execution_time_ms,
                        "metrics": fallback_result.metrics,
                        "data": fallback_result.data,
                        "fallback_used": True,
                        "error": str(e),
                    }

                    return fallback_result

                except Exception as fallback_error:
                    # Both main and fallback failed
                    error_result = StageResult(
                        success=False,
                        data=None,
                        metrics={},
                        error=(
                            f"Stage failed: {str(e)}, "
                            f"Fallback failed: {str(fallback_error)}"
                        ),
                        execution_time_ms=(time.time() - start_time) * 1000,
                    )

                    # Log complete failure if trace context is available
                    if trace_ctx:
                        trace_ctx.log_stage_end(
                            stage_name=self.name,
                            output_text="",
                            changes=[],
                            metrics={},
                            error={
                                "type": "CompleteFailure",
                                "message": (
                                    f"Main: {str(e)}, Fallback: {str(fallback_error)}"
                                ),
                                "fallback": "failed",
                                "impact": "stage_unavailable",
                            },
                        )

                    context.stage_metrics[self.name] = {
                        "success": False,
                        "execution_time_ms": error_result.execution_time_ms,
                        "error": str(e),
                    }

                    return error_result

    def validate_input(self, context: StageContext) -> bool:
        """
        Validate input context before processing.

        Args:
            context: Pipeline context

        Returns:
            True if input is valid
        """
        return context is not None and context.original_content is not None

    def get_stage_config(self, context: StageContext) -> Dict[str, Any]:
        """
        Get stage-specific configuration.

        Args:
            context: Pipeline context

        Returns:
            Stage configuration dictionary
        """
        return context.config.get("stages", {}).get(self.name, {})

    def add_debug_info(
        self, context: StageContext, message: str, data: Any = None
    ) -> None:
        """
        Add debug information to context.

        Args:
            context: Pipeline context
            message: Debug message
            data: Optional debug data
        """
        if context.debug_enabled:
            debug_info = {
                "stage": self.name,
                "message": message,
                "timestamp": time.time(),
                "data": data,
            }

            if "debug_trace" not in context.stage_metrics:
                context.stage_metrics["debug_trace"] = []

            context.stage_metrics["debug_trace"].append(debug_info)

    def _get_input_text(self, context: StageContext) -> str:
        """
        Extract input text for tracing from context.

        Args:
            context: Pipeline context

        Returns:
            Input text for the stage
        """
        # Default to original content
        if hasattr(context, "original_content") and context.original_content:
            return context.original_content

        # Try to get from previous stage output
        if self.name == "security_processing":
            return context.original_content or ""
        elif hasattr(context, "optimized_prompt") and context.optimized_prompt:
            return context.optimized_prompt
        elif hasattr(context, "compiled_prompt") and context.compiled_prompt:
            return context.compiled_prompt
        else:
            return ""

    def _get_output_text(self, context: StageContext, result: StageResult) -> str:
        """
        Extract output text for tracing from context and result.

        Args:
            context: Pipeline context
            result: Stage execution result

        Returns:
            Output text from the stage
        """
        # Try to get from context first (for stages that update context)
        if self.name == "security_processing" and hasattr(context, "security_result"):
            if context.security_result:
                return get_sanitized_content(
                    context.security_result, context.original_content or ""
                )
        elif self.name == "ir_generation" and hasattr(context, "ir"):
            if context.ir and hasattr(context.ir, "to_text"):
                return context.ir.to_text()
        elif self.name == "compilation" and hasattr(context, "compiled_prompt"):
            return context.compiled_prompt
        elif self.name == "optimization" and hasattr(context, "optimized_prompt"):
            return context.optimized_prompt
        elif self.name == "generation" and hasattr(context, "model_response"):
            return context.model_response

        # Try to get from result data
        if result.data:
            if isinstance(result.data, str):
                return result.data
            elif hasattr(result.data, "sanitized_content"):
                return result.data.sanitized_content
            elif hasattr(result.data, "to_text"):
                return result.data.to_text()
            elif hasattr(result.data, "response"):
                return result.data.response

        # Fallback to empty string
        return ""

    def _extract_changes(self, context: StageContext, result: StageResult) -> List:
        """
        Extract changes made during stage execution for tracing.

        Args:
            context: Pipeline context
            result: Stage execution result

        Returns:
            List of changes made during the stage
        """
        changes = []

        # Extract PII changes from security stage
        if self.name == "security_processing" and hasattr(context, "security_result"):
            if context.security_result and hasattr(
                context.security_result, "pii_entities"
            ):
                for entity in context.security_result.pii_entities:
                    from ...core.trace_context import StageChange

                    changes.append(
                        StageChange(
                            type=entity.entity_type,
                            original=entity.original_text,
                            modified=entity.masked_text,
                            confidence=getattr(entity, "confidence", None),
                            metadata={"start": entity.start,
                                      "end": entity.end},
                        )
                    )

        # Extract optimization changes
        if self.name == "optimization" and result.metrics:
            if "tokens_saved" in result.metrics:
                from ...core.trace_context import StageChange

                changes.append(
                    StageChange(
                        type="token_optimization",
                        original=f"tokens_before: {result.metrics.get('tokens_before', 'unknown')}",
                        modified=f"tokens_after: {result.metrics.get('tokens_after', 'unknown')}",
                        metadata=result.metrics,
                    )
                )

        # Extract changes from result data
        if result.data and hasattr(result.data, "changes"):
            for change in result.data.changes:
                from ...core.trace_context import StageChange

                changes.append(
                    StageChange(
                        type=change.get("type", "unknown"),
                        original=change.get("original", ""),
                        modified=change.get("modified", ""),
                        confidence=change.get("confidence"),
                        metadata=change.get("metadata", {}),
                    )
                )

        return changes
