"""
IR Generation Stage - Stage 2 of the pipeline

Converts content to Intermediate Representation with intent analysis.
"""

from typing import Dict, Any
from ..components.stage_base import StageBase, StageResult, StageContext
from ...security.service import get_sanitized_content
from ..policy_gate import modification_disabled


class IRGenerationStage(StageBase):
    """
    IR generation stage for converting content to structured representation.

    This stage handles:
    - Intent extraction and classification
    - Entity recognition
    - Constraint identification
    - Complexity analysis
    - IR creation and validation
    """

    def __init__(self):
        """Initialize IR generation stage."""
        super().__init__("ir_generation")
        self.ir_builder = None

    def _initialize_components(self, context: StageContext):
        """Initialize IR builder component."""
        if self.ir_builder is None:
            try:
                from ...ir.ir_builder import IRBuilder

                self.ir_builder = IRBuilder()
            except ImportError as e:
                if context.debug_enabled:
                    print(
                        f"[IR Generation] Failed to initialize IRBuilder: {e}")
                raise

    def execute(self, context: StageContext) -> StageResult:
        """
        Generate Intermediate Representation from content.

        Args:
            context: Pipeline context with security-processed content

        Returns:
            StageResult with generated IR
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
                data=None,
                metrics={"ir_skipped": True, "modification_disabled": True},
            )

        # Initialize components
        if self.ir_builder is None:
            self._initialize_components(context)

        # Get input content (use sanitized content if privacy enabled)
        if context.config.get("privacy", True) and context.security_result:
            content = get_sanitized_content(
                context.security_result, context.original_content
            )
        else:
            content = context.original_content

        input_size = len(content)

        # Generate IR
        ir = self.ir_builder.parse(content)

        # Validate IR
        validation_result = self._validate_ir(ir)

        # Add debug information
        self.add_debug_info(
            context,
            "IR generation completed",
            {
                "intent": ir.intent.value if hasattr(ir, "intent") else "unknown",
                "complexity": (
                    ir.get_complexity_level()
                    if hasattr(ir, "get_complexity_level")
                    else "unknown"
                ),
                "validation_passed": validation_result["valid"],
            },
        )

        # Store result in context
        context.ir = ir

        # Calculate metrics
        custom_metrics = {
            "intent": ir.intent.value if hasattr(ir, "intent") else "unknown",
            "entity": ir.entity.value if hasattr(ir, "entity") else "unknown",
            "complexity_level": (
                ir.get_complexity_level()
                if hasattr(ir, "get_complexity_level")
                else "unknown"
            ),
            "validation_passed": validation_result["valid"],
            "validation_errors": len(validation_result.get("errors", [])),
            "extracted_entities": len(getattr(ir, "extracted_entities", [])),
            "constraints": len(getattr(ir, "constraints", [])),
        }

        return StageResult(
            success=validation_result["valid"], data=ir, metrics=custom_metrics
        )

    def _validate_ir(self, ir) -> Dict[str, Any]:
        """Validate generated IR for completeness and correctness."""
        errors = []
        warnings = []

        # Check required attributes
        required_attrs = [
            "intent",
            "entity",
            "constraints",
            "privacy",
            "original_prompt",
        ]
        for attr in required_attrs:
            if not hasattr(ir, attr):
                errors.append(f"Missing required attribute: {attr}")
            elif getattr(ir, attr) is None:
                errors.append(f"Required attribute is None: {attr}")

        # Check intent validity
        if hasattr(ir, "intent"):
            try:
                from ...ir.prompt_ir import IntentType

                valid_intents = [intent.value for intent in IntentType]
                if ir.intent.value not in valid_intents:
                    errors.append(f"Invalid intent: {ir.intent.value}")
            except ImportError:
                warnings.append("Could not validate intent types")

        # Check entity validity
        if hasattr(ir, "entity"):
            try:
                from ...ir.prompt_ir import EntityType

                valid_entities = [entity.value for entity in EntityType]
                if ir.entity.value not in valid_entities:
                    errors.append(f"Invalid entity: {ir.entity.value}")
            except ImportError:
                warnings.append("Could not validate entity types")

        # Check for empty content
        if hasattr(ir, "original_prompt") and not ir.original_prompt.strip():
            errors.append("Original prompt is empty")

        # Check complexity level
        if hasattr(ir, "get_complexity_level"):
            complexity = ir.get_complexity_level()
            if complexity not in ["low", "medium", "high"]:
                warnings.append(f"Unknown complexity level: {complexity}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback IR generation if main processing fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback IR
        """
        # Get input content
        if context.config.get("privacy", True) and context.security_result:
            content = get_sanitized_content(
                context.security_result, context.original_content
            )
        else:
            content = context.original_content

        # Create minimal fallback IR
        try:
            from ...ir.prompt_ir import (
                PromptIR,
                IntentType,
                EntityType,
                ConstraintType,
                PrivacyLevel,
            )

            fallback_ir = PromptIR(
                intent=IntentType.ANALYZE,  # Default intent
                entity=EntityType.TEXT,  # Default entity
                constraints=[ConstraintType.ACCURACY],  # Default constraint
                privacy=PrivacyLevel.INTERNAL,  # Default privacy
                original_prompt=content,
                extracted_entities=[],  # No entities extracted
                parameters={},  # No parameters
            )

            # Set basic attributes
            fallback_ir.token_estimate = len(content.split())
            fallback_ir.optimization_targets = context.config.get(
                "optimization_targets", ["tokens", "accuracy"]
            )

        except ImportError:
            # Create minimal IR object if imports fail
            fallback_ir = type(
                "FallbackIR",
                (),
                {
                    "to_dict": lambda: {
                        "intent": "analyze",
                        "entity": "text",
                        "content": content,
                    },
                    "get_complexity_level": lambda: "medium",
                    "intent": type("Intent", (), {"value": "analyze"})(),
                    "entity": type("Entity", (), {"value": "text"})(),
                    "original_prompt": content,
                    "token_estimate": len(content.split()),
                },
            )()

        context.ir = fallback_ir

        self.add_debug_info(
            context,
            "IR fallback used",
            {"reason": "main_ir_generation_failed", "fallback_type": "minimal_ir"},
        )

        return StageResult(
            success=True,
            data=fallback_ir,
            metrics={
                "fallback_used": True,
                "intent": "analyze",
                "complexity_level": "medium",
            },
        )

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for IR generation."""
        if not super().validate_input(context):
            return False

        # Check if security processing was completed
        if context.config.get("privacy", True) and not context.security_result:
            if context.debug_enabled:
                print("[IR Generation] Security result required but not available")
            return False

        return True
