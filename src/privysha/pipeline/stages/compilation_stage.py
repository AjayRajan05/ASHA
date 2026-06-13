"""
Prompt Compilation Stage - Stage 4 of the pipeline

Compiles IR into optimized prompt format.
"""

from typing import Dict, Any, Optional, cast
from ..components.stage_base import StageBase, StageResult, StageContext
from ..policy_gate import modification_disabled
from ...security.service import get_sanitized_content


class CompilationStage(StageBase):
    """
    Prompt compilation stage for IR to prompt conversion.

    This stage handles:
    - IR to prompt compilation
    - Template application
    - Format optimization
    - Structure validation
    """

    def __init__(self) -> None:
        """Initialize prompt compilation stage."""
        super().__init__("prompt_compilation")
        self.prompt_compiler: Optional[Any] = None

    def _initialize_components(self, context: StageContext) -> None:
        """Initialize prompt compiler component."""
        if self.prompt_compiler is None:
            try:
                from ...compiler.prompt_compiler import PromptCompiler

                self.prompt_compiler = PromptCompiler()
            except ImportError as e:
                if context.debug_enabled:
                    print(
                        f"[Prompt Compilation] Failed to initialize PromptCompiler: {e}"
                    )
                raise

    def execute(self, context: StageContext) -> StageResult:
        """
        Compile IR into optimized prompt.

        Args:
            context: Pipeline context with IR and routing decision

        Returns:
            StageResult with compiled prompt
        """
        if modification_disabled(context.config):
            content = context.original_content
            if context.config.get("privacy", True) and context.security_result:
                content = get_sanitized_content(
                    context.security_result, context.original_content
                )
            context.compiled_prompt = content
            return StageResult(
                success=True,
                data=content,
                metrics={"compilation_skipped": True, "modification_disabled": True},
            )

        # Initialize components
        if self.prompt_compiler is None:
            self._initialize_components(context)

        assert self.prompt_compiler is not None

        # Validate input
        if not context.ir:
            raise ValueError("IR is required for prompt compilation")

        input_size = (
            len(str(context.ir.to_dict()))
            if hasattr(context.ir, "to_dict")
            else len(str(context.ir))
        )

        # Determine optimization level based on routing decision
        optimization_level = self._determine_optimization_level(context)

        # Compile prompt
        compiled_prompt = self.prompt_compiler.compile(
            context.ir, optimization_level=optimization_level
        )

        # Validate compiled prompt
        validation_result = self._validate_compiled_prompt(compiled_prompt)

        # Add debug information
        self.add_debug_info(
            context,
            "Prompt compilation completed",
            {
                "optimization_level": optimization_level,
                "prompt_length": len(compiled_prompt),
                "validation_passed": validation_result["valid"],
            },
        )

        # Store result in context
        context.compiled_prompt = compiled_prompt

        # Calculate metrics
        custom_metrics = {
            "optimization_level": optimization_level,
            "compiled_prompt_length": len(compiled_prompt),
            "validation_passed": validation_result["valid"],
            "validation_errors": len(validation_result.get("errors", [])),
            "tokens_estimate": len(compiled_prompt.split()),
        }

        # Add compilation-specific metrics
        if hasattr(context.ir, "intent"):
            custom_metrics["intent"] = context.ir.intent.value

        if hasattr(context.ir, "complexity"):
            custom_metrics["ir_complexity"] = context.ir.complexity

        return StageResult(
            success=validation_result["valid"],
            data=compiled_prompt,
            metrics=custom_metrics,
        )

    def _determine_optimization_level(self, context: StageContext) -> str:
        """Determine optimization level based on context."""
        # Check routing decision for hints
        if context.routing_decision:
            model = getattr(context.routing_decision, "selected_model", None)
            if model and hasattr(model, "capabilities"):
                capabilities = model.capabilities
                if "code" in capabilities:
                    return "code_optimized"
                elif "analysis" in capabilities:
                    return "analysis_optimized"

        # Check IR complexity
        if context.ir and hasattr(context.ir, "get_complexity_level"):
            complexity = context.ir.get_complexity_level()
            if complexity == "high":
                return "comprehensive"
            elif complexity == "low":
                return "minimal"

        # Check configuration
        config_level = context.config.get("compilation_level")
        if config_level:
            return cast(str, config_level)

        # Default to standard
        return "standard"

    def _validate_compiled_prompt(self, compiled_prompt: str) -> Dict[str, Any]:
        """Validate compiled prompt for quality and completeness."""
        errors = []
        warnings = []

        # Check for empty prompt
        if not compiled_prompt or not compiled_prompt.strip():
            errors.append("Compiled prompt is empty")

        # Check for minimum length
        if len(compiled_prompt.strip()) < 10:
            warnings.append("Compiled prompt is very short")

        # Check for maximum length
        if len(compiled_prompt) > 10000:
            warnings.append("Compiled prompt is very long")

        # Check for basic structure
        if not any(char in compiled_prompt for char in [".", "?", "!"]):
            warnings.append("Compiled prompt lacks proper punctuation")

        # Check for common compilation issues
        if "{" in compiled_prompt and "}" not in compiled_prompt:
            errors.append("Unclosed template brackets")

        if compiled_prompt.count("{") != compiled_prompt.count("}"):
            errors.append("Mismatched template brackets")

        # Check for repeated content
        words = compiled_prompt.split()
        if len(words) > 10:
            repeated_words = [word for word in set(
                words) if words.count(word) > 3]
            if repeated_words:
                warnings.append(
                    f"Repeated words detected: {repeated_words[:3]}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback prompt compilation if main processing fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback compiled prompt
        """
        # Create minimal fallback prompt
        if context.ir and hasattr(context.ir, "original_prompt"):
            fallback_prompt = context.ir.original_prompt
        else:
            fallback_prompt = context.original_content

        # Basic cleanup
        fallback_prompt = fallback_prompt.strip()
        if not fallback_prompt.endswith((".", "?", "!")):
            fallback_prompt += "."

        context.compiled_prompt = fallback_prompt

        self.add_debug_info(
            context,
            "Prompt compilation fallback used",
            {"reason": "main_compilation_failed",
                "fallback_type": "original_content"},
        )

        return StageResult(
            success=True,
            data=fallback_prompt,
            metrics={
                "fallback_used": True,
                "optimization_level": "none",
                "compiled_prompt_length": len(fallback_prompt),
                "tokens_estimate": len(fallback_prompt.split()),
            },
        )

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for prompt compilation."""
        if not super().validate_input(context):
            return False

        # Check if IR is available
        if not context.ir:
            if context.debug_enabled:
                print("[Prompt Compilation] IR is required but not available")
            return False

        return True
