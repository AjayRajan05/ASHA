"""
Model Generation Stage - Stage 6 of the pipeline

Handles LLM API integration and response generation.
"""

from typing import Dict, Any, Optional
from ..components.stage_base import StageBase, StageResult, StageContext


class GenerationStage(StageBase):
    """
    Model generation stage for LLM API integration.

    This stage handles:
    - LLM API integration
    - Response generation
    - Error handling
    - Timeout management
    - Response validation
    """

    def __init__(self):
        """Initialize model generation stage."""
        super().__init__("model_generation")
        self.universal_adapter = None

    def _initialize_components(self, context: StageContext):
        """Initialize universal adapter component."""
        # Universal adapter is optional - provided by caller

    def execute(self, context: StageContext) -> StageResult:
        """
        Generate model response using optimized prompt.

        Args:
            context: Pipeline context with optimized prompt

        Returns:
            StageResult with model response
        """
        # Get adapter from context or use default
        adapter = context.config.get("model_adapter")

        if not adapter:
            # No adapter provided - skip generation
            self.add_debug_info(
                context, "No model adapter provided - skipping generation"
            )
            return StageResult(
                success=True,
                data=None,
                metrics={"skipped": True, "reason": "no_adapter"},
            )

        # Validate input
        if not context.optimized_prompt:
            raise ValueError(
                "Optimized prompt is required for model generation")

        input_size = len(context.optimized_prompt)

        # Generate response
        response = self._generate_response(
            adapter, context.optimized_prompt, context)

        # Validate response
        validation_result = self._validate_response(response)

        # Add debug information
        self.add_debug_info(
            context,
            "Model generation completed",
            {
                "response_length": len(response) if response else 0,
                "adapter_type": type(adapter).__name__,
                "validation_passed": validation_result["valid"],
            },
        )

        # Store result in context
        context.model_response = response

        # Calculate metrics
        custom_metrics = {
            "response_length": len(response) if response else 0,
            "adapter_type": type(adapter).__name__,
            "validation_passed": validation_result["valid"],
            "validation_errors": len(validation_result.get("errors", [])),
        }

        # Add response-specific metrics
        if response:
            custom_metrics.update(
                {
                    "response_tokens": len(response.split()),
                    "response_sentences": len(
                        [s.strip() for s in response.split(".") if s.strip()]
                    ),
                }
            )

        return StageResult(
            success=validation_result["valid"], data=response, metrics=custom_metrics
        )

    def _generate_response(
        self, adapter, prompt: str, context: StageContext
    ) -> Optional[str]:
        """Generate response using the provided adapter."""
        try:
            # Get timeout from config
            timeout = context.config.get("generation_timeout", 60)

            # Generate response
            response = adapter.generate(prompt, timeout=timeout)

            return response

        except Exception as e:
            if context.debug_enabled:
                print(f"[Generation] Failed to generate response: {e}")

            # Return None on generation failure
            return None

    def _validate_response(self, response: Optional[str]) -> Dict[str, Any]:
        """Validate generated response."""
        errors = []
        warnings = []

        if response is None:
            warnings.append("No response generated")
            return {"valid": True, "errors": errors, "warnings": warnings}

        # Check for empty response
        if not response or not response.strip():
            warnings.append("Response is empty")

        # Check for extremely short response
        if len(response.strip()) < 5:
            warnings.append("Response is very short")

        # Check for extremely long response
        if len(response) > 50000:  # 50KB limit
            warnings.append("Response is very long")

        # Check for common error patterns
        error_patterns = [
            "error",
            "failed",
            "unable",
            "cannot",
            "sorry",
            "i cannot",
            "i am unable",
            "i don't understand",
        ]

        response_lower = response.lower()
        if any(pattern in response_lower for pattern in error_patterns):
            warnings.append("Response may contain error message")

        # Check for repeated content
        words = response.split()
        if len(words) > 20:
            repeated_words = [word for word in set(
                words) if words.count(word) > 5]
            if repeated_words:
                warnings.append(
                    f"Repeated words in response: {repeated_words[:3]}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback generation if main processing fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback response
        """
        fallback_response = None

        # Try to get a simple response if adapter is available
        adapter = context.config.get("model_adapter")
        if adapter and context.optimized_prompt:
            try:
                # Simple retry with shorter timeout
                fallback_response = adapter.generate(
                    context.optimized_prompt, timeout=10
                )
            except Exception:
                pass

        if not fallback_response:
            # Create a placeholder response
            fallback_response = "Unable to generate response due to processing error."

        context.model_response = fallback_response

        self.add_debug_info(
            context,
            "Generation fallback used",
            {
                "reason": "main_generation_failed",
                "fallback_type": "placeholder_response",
            },
        )

        return StageResult(
            success=True,
            data=fallback_response,
            metrics={
                "fallback_used": True,
                "response_length": len(fallback_response),
                "adapter_type": "fallback",
            },
        )

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for model generation."""
        if not super().validate_input(context):
            return False

        # Check if optimized prompt is available
        if not context.optimized_prompt:
            if context.debug_enabled:
                print("[Generation] Optimized prompt is required but not available")
            return False

        return True
