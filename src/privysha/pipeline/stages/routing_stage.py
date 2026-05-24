"""
Model Routing Stage - Stage 3 of the pipeline

Intelligent model selection based on IR analysis.
"""

from typing import Dict, Any
from ..components.stage_base import StageBase, StageResult, StageContext


class RoutingStage(StageBase):
    """
    Model routing stage for intelligent model selection.

    This stage handles:
    - Model selection based on IR analysis
    - Cost optimization routing
    - Performance-based routing
    - Confidence scoring
    - Fallback routing strategies
    """

    def __init__(self):
        """Initialize model routing stage."""
        super().__init__("model_routing")
        self.model_router = None

    def _initialize_components(self, context: StageContext):
        """Initialize model router component."""
        if self.model_router is None:
            try:
                from ...routing.model_router import ModelRouter, RoutingStrategy

                # Get routing strategy from config
                routing_strategy = context.config.get(
                    "routing_strategy", "HYBRID")
                if isinstance(routing_strategy, str):
                    routing_strategy = RoutingStrategy[routing_strategy.upper(
                    )]

                self.model_router = ModelRouter(
                    default_strategy=routing_strategy)
            except ImportError as e:
                if context.debug_enabled:
                    print(
                        f"[Model Routing] Failed to initialize ModelRouter: {e}")
                raise

    def execute(self, context: StageContext) -> StageResult:
        """
        Perform intelligent model routing based on IR.

        Args:
            context: Pipeline context with generated IR

        Returns:
            StageResult with routing decision
        """
        # Initialize components
        if self.model_router is None:
            self._initialize_components(context)

        # Validate input
        if not context.ir:
            raise ValueError("IR is required for model routing")

        input_size = (
            len(str(context.ir.to_dict()))
            if hasattr(context.ir, "to_dict")
            else len(str(context.ir))
        )

        # Get routing constraints
        constraints = context.config.get("routing_constraints", {})

        # Perform model routing
        routing_decision = self.model_router.route(
            context.ir, constraints=constraints)

        # Validate routing decision
        validation_result = self._validate_routing_decision(routing_decision)

        # Add debug information
        self.add_debug_info(
            context,
            "Model routing completed",
            {
                "selected_model": getattr(
                    routing_decision.selected_model, "name", "unknown"
                ),
                "provider": getattr(
                    routing_decision.selected_model, "provider", "unknown"
                ),
                "confidence": getattr(routing_decision, "confidence_score", 0.0),
                "estimated_cost": getattr(routing_decision, "estimated_cost", 0.0),
                "validation_passed": validation_result["valid"],
            },
        )

        # Store result in context
        context.routing_decision = routing_decision

        # Calculate metrics
        custom_metrics = {
            "selected_model": getattr(
                routing_decision.selected_model, "name", "unknown"
            ),
            "provider": getattr(routing_decision.selected_model, "provider", "unknown"),
            "confidence_score": getattr(routing_decision, "confidence_score", 0.0),
            "estimated_cost": getattr(routing_decision, "estimated_cost", 0.0),
            "reasoning": getattr(routing_decision, "reasoning", "unknown"),
            "validation_passed": validation_result["valid"],
            "validation_errors": len(validation_result.get("errors", [])),
        }

        # Add model-specific metrics if available
        if hasattr(routing_decision.selected_model, "capabilities"):
            custom_metrics["model_capabilities"] = (
                routing_decision.selected_model.capabilities
            )

        if hasattr(routing_decision.selected_model, "pricing"):
            custom_metrics["model_pricing"] = routing_decision.selected_model.pricing

        return StageResult(
            success=validation_result["valid"],
            data=routing_decision,
            metrics=custom_metrics,
        )

    def _validate_routing_decision(self, routing_decision) -> Dict[str, Any]:
        """Validate routing decision for completeness."""
        errors = []
        warnings = []

        # Check required attributes
        required_attrs = ["selected_model", "confidence_score", "reasoning"]
        for attr in required_attrs:
            if not hasattr(routing_decision, attr):
                errors.append(f"Missing required attribute: {attr}")
            elif getattr(routing_decision, attr) is None:
                errors.append(f"Required attribute is None: {attr}")

        # Check selected model
        if hasattr(routing_decision, "selected_model"):
            model = routing_decision.selected_model
            if not hasattr(model, "name"):
                errors.append("Selected model missing name attribute")
            elif not model.name:
                errors.append("Selected model name is empty")

            if not hasattr(model, "provider"):
                warnings.append("Selected model missing provider attribute")

        # Check confidence score
        if hasattr(routing_decision, "confidence_score"):
            confidence = routing_decision.confidence_score
            if (
                not isinstance(confidence, (int, float))
                or confidence < 0
                or confidence > 1
            ):
                errors.append(f"Invalid confidence score: {confidence}")
            elif confidence < 0.3:
                warnings.append(f"Low confidence score: {confidence}")

        # Check estimated cost
        if hasattr(routing_decision, "estimated_cost"):
            cost = routing_decision.estimated_cost
            if not isinstance(cost, (int, float)) or cost < 0:
                warnings.append(f"Invalid estimated cost: {cost}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def fallback(self, context: StageContext) -> StageResult:
        """
        Fallback model routing if main processing fails.

        Args:
            context: Pipeline context

        Returns:
            StageResult with fallback routing decision
        """
        # Create minimal fallback routing decision
        fallback_decision = type(
            "FallbackRoutingDecision",
            (),
            {
                "selected_model": type(
                    "Model",
                    (),
                    {
                        "name": "default",
                        "provider": "unknown",
                        "capabilities": ["text"],
                        "pricing": {"input_tokens": 0.001, "output_tokens": 0.002},
                    },
                )(),
                "confidence_score": 0.5,
                "reasoning": "fallback routing",
                "estimated_cost": 0.01,
            },
        )()

        context.routing_decision = fallback_decision

        self.add_debug_info(
            context,
            "Model routing fallback used",
            {"reason": "main_routing_failed", "fallback_model": "default"},
        )

        return StageResult(
            success=True,
            data=fallback_decision,
            metrics={
                "fallback_used": True,
                "selected_model": "default",
                "provider": "unknown",
                "confidence_score": 0.5,
            },
        )

    def validate_input(self, context: StageContext) -> bool:
        """Validate input for model routing."""
        if not super().validate_input(context):
            return False

        # Check if IR is available
        if not context.ir:
            if context.debug_enabled:
                print("[Model Routing] IR is required but not available")
            return False

        return True
