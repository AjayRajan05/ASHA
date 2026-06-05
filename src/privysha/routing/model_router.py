# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time
from ..ir.prompt_ir import PromptIR, IntentType, EntityType


class RoutingStrategy(Enum):
    """Routing strategies for model selection."""

    TASK_BASED = "task_based"
    COST_BASED = "cost_based"
    PERFORMANCE_BASED = "performance_based"
    AVAILABILITY_BASED = "availability_based"
    HYBRID = "hybrid"
    LOCAL_PRIVACY = "local_privacy"


class ModelCapability(Enum):
    """Model capability levels."""

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    SPECIALIZED = "specialized"


@dataclass
class ModelConfig:
    """Configuration for a model."""

    name: str
    provider: str
    capability: ModelCapability
    cost_per_1k_tokens: float
    avg_latency_ms: int
    max_tokens: int
    supports_streaming: bool
    reliability_score: float
    specializations: List[str]
    current_load: float = 0.0
    last_health_check: float = 0.0


@dataclass
class RoutingDecision:
    """Result of routing decision."""

    selected_model: ModelConfig
    routing_strategy: RoutingStrategy
    confidence_score: float
    reasoning: str
    alternative_models: List[ModelConfig]
    estimated_cost: float
    estimated_latency: int


class ModelRouter:
    """
    Intelligent Multi-Model Router for PrivySHA.

    Automatically selects the best model based on:
    - Task type and complexity
    - Cost constraints
    - Performance requirements
    - Model availability and load
    - Specialization requirements
    """

    def __init__(self, default_strategy: RoutingStrategy = RoutingStrategy.HYBRID):
        """Initialize model router with strategy."""
        self.default_strategy = default_strategy
        self.model_registry = self._init_model_registry()
        self.routing_weights = self._init_routing_weights()
        self.performance_cache = {}
        self.cost_models = self._init_cost_models()
        self.load_balancer = LoadBalancer()
        self._local_advisor_report = None

    def _init_model_registry(self) -> Dict[str, ModelConfig]:
        """Initialize model registry with available models."""
        return {
            # OpenAI Models
            "gpt-4o-mini": ModelConfig(
                name="gpt-4o-mini",
                provider="openai",
                capability=ModelCapability.STANDARD,
                cost_per_1k_tokens=0.00015,
                avg_latency_ms=800,
                max_tokens=128000,
                supports_streaming=True,
                reliability_score=0.95,
                specializations=["general", "analysis", "generation"],
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                provider="openai",
                capability=ModelCapability.ADVANCED,
                cost_per_1k_tokens=0.005,
                avg_latency_ms=1200,
                max_tokens=128000,
                supports_streaming=True,
                reliability_score=0.97,
                specializations=["complex_analysis", "reasoning", "coding"],
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                capability=ModelCapability.BASIC,
                cost_per_1k_tokens=0.0005,
                avg_latency_ms=600,
                max_tokens=16385,
                supports_streaming=True,
                reliability_score=0.90,
                specializations=["chat", "simple_tasks", "high_volume"],
            ),
            # Anthropic Models
            "claude-3-haiku": ModelConfig(
                name="claude-3-haiku",
                provider="anthropic",
                capability=ModelCapability.STANDARD,
                cost_per_1k_tokens=0.00025,
                avg_latency_ms=700,
                max_tokens=200000,
                supports_streaming=True,
                reliability_score=0.93,
                specializations=["fast_analysis", "coding", "general"],
            ),
            "claude-3-sonnet": ModelConfig(
                name="claude-3-sonnet",
                provider="anthropic",
                capability=ModelCapability.ADVANCED,
                cost_per_1k_tokens=0.003,
                avg_latency_ms=1000,
                max_tokens=200000,
                supports_streaming=True,
                reliability_score=0.96,
                specializations=["complex_reasoning", "analysis", "writing"],
            ),
            "claude-3-opus": ModelConfig(
                name="claude-3-opus",
                provider="anthropic",
                capability=ModelCapability.SPECIALIZED,
                cost_per_1k_tokens=0.015,
                avg_latency_ms=1500,
                max_tokens=200000,
                supports_streaming=True,
                reliability_score=0.94,
                specializations=["expert_analysis",
                                 "creative_writing", "research"],
            ),
            # Grok Models
            "grok-beta": ModelConfig(
                name="grok-beta",
                provider="grok",
                capability=ModelCapability.ADVANCED,
                cost_per_1k_tokens=0.0005,
                avg_latency_ms=900,
                max_tokens=131072,
                supports_streaming=True,
                reliability_score=0.88,
                specializations=["real_time", "current_events", "analysis"],
            ),
            # Local Models (Ollama)
            "llama3-8b": ModelConfig(
                name="llama3-8b",
                provider="ollama",
                capability=ModelCapability.STANDARD,
                cost_per_1k_tokens=0.0,  # Free for local
                avg_latency_ms=2000,
                max_tokens=8192,
                supports_streaming=True,
                reliability_score=0.85,
                specializations=["privacy", "cost_sensitive", "general"],
            ),
            "codellama-7b": ModelConfig(
                name="codellama-7b",
                provider="ollama",
                capability=ModelCapability.SPECIALIZED,
                cost_per_1k_tokens=0.0,
                avg_latency_ms=2500,
                max_tokens=16384,
                supports_streaming=True,
                reliability_score=0.82,
                specializations=["coding", "debugging", "technical"],
            ),
        }

    def _init_routing_weights(self) -> Dict[str, float]:
        """Initialize routing decision weights."""
        return {
            "task_match": 0.3,
            "cost_efficiency": 0.25,
            "performance": 0.2,
            "availability": 0.15,
            "specialization": 0.1,
        }

    def _init_cost_models(self) -> Dict[str, Dict[str, float]]:
        """Initialize cost models for different providers."""
        return {
            "openai": {
                "gpt-4o-mini": 0.00015,
                "gpt-4o": 0.005,
                "gpt-3.5-turbo": 0.0005,
            },
            "anthropic": {
                "claude-3-haiku": 0.00025,
                "claude-3-sonnet": 0.003,
                "claude-3-opus": 0.015,
            },
            "grok": {"grok-beta": 0.0005},
            "ollama": {"llama3-8b": 0.0, "codellama-7b": 0.0},
        }

    def route(
        self,
        ir: PromptIR,
        strategy: RoutingStrategy = None,
        constraints: Dict[str, Any] = None,
    ) -> RoutingDecision:
        """
        Route prompt to optimal model.

        Args:
            ir: Prompt Intermediate Representation
            strategy: Routing strategy (uses default if None)
            constraints: Additional routing constraints

        Returns:
            RoutingDecision with selected model and reasoning
        """
        if strategy is None:
            strategy = self.default_strategy

        if constraints is None:
            constraints = {}

        strategy = self._resolve_strategy(ir, strategy, constraints)

        if strategy == RoutingStrategy.LOCAL_PRIVACY:
            local_decision = self._route_local_privacy(ir, constraints)
            if local_decision:
                return local_decision

        # Get candidate models
        candidates = self._get_candidate_models(ir, constraints)

        # Score candidates based on strategy
        scored_candidates = self._score_candidates(
            candidates, ir, strategy, constraints
        )

        # Select best model
        selected_model, confidence, reasoning = self._select_best_model(
            scored_candidates, strategy
        )

        # Get alternatives
        alternatives = self._get_alternatives(
            scored_candidates, selected_model)

        # Calculate estimates
        estimated_cost = self._estimate_cost(selected_model, ir)
        estimated_latency = self._estimate_latency(selected_model, ir)

        return RoutingDecision(
            selected_model=selected_model,
            routing_strategy=strategy,
            confidence_score=confidence,
            reasoning=reasoning,
            alternative_models=alternatives,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
        )

    def _get_candidate_models(
        self, ir: PromptIR, constraints: Dict[str, Any]
    ) -> List[ModelConfig]:
        """Get candidate models based on basic requirements."""
        candidates = []

        for model in self.model_registry.values():
            # Check basic capability requirements
            if not self._meets_capability_requirements(model, ir):
                continue

            # Check token limits
            if ir.token_estimate and ir.token_estimate > model.max_tokens:
                continue

            # Check constraint requirements
            if not self._meets_constraint_requirements(model, ir, constraints):
                continue

            # Check availability
            if not self._is_model_available(model):
                continue

            candidates.append(model)

        return candidates if candidates else list(self.model_registry.values())

    def _meets_capability_requirements(self, model: ModelConfig, ir: PromptIR) -> bool:
        """Check if model meets capability requirements."""
        complexity_level = ir.get_complexity_level()

        # Map complexity to required capability
        capability_requirements = {
            "low": [
                ModelCapability.BASIC,
                ModelCapability.STANDARD,
                ModelCapability.ADVANCED,
                ModelCapability.SPECIALIZED,
            ],
            "medium": [
                ModelCapability.STANDARD,
                ModelCapability.ADVANCED,
                ModelCapability.SPECIALIZED,
            ],
            "high": [ModelCapability.ADVANCED, ModelCapability.SPECIALIZED],
        }

        required_capabilities = capability_requirements.get(
            complexity_level, [ModelCapability.STANDARD]
        )
        return model.capability in required_capabilities

    def _meets_constraint_requirements(
        self, model: ModelConfig, ir: PromptIR, constraints: Dict[str, Any]
    ) -> bool:
        """Check if model meets constraint requirements."""
        # Cost constraints
        if ir.is_cost_sensitive() and model.cost_per_1k_tokens > 0.01:
            return False

        # Speed constraints
        if ir.is_time_sensitive() and model.avg_latency_ms > 2000:
            return False

        # Privacy constraints — prefer local when forced
        if constraints.get("force_local") and model.provider != "ollama":
            return False

        # Specialization requirements
        if ir.entity == EntityType.CODE and "coding" not in model.specializations:
            # Prefer coding-specialized models for code tasks
            pass  # Not a hard requirement, just preference

        # Custom constraints
        max_cost = constraints.get("max_cost_per_1k")
        if max_cost and model.cost_per_1k_tokens > max_cost:
            return False

        max_latency = constraints.get("max_latency_ms")
        if max_latency and model.avg_latency_ms > max_latency:
            return False

        required_provider = constraints.get("provider")
        if required_provider and model.provider != required_provider:
            return False

        return True

    def _is_model_available(self, model: ModelConfig) -> bool:
        """Check if model is currently available."""
        # Check if model is under maintenance
        if model.reliability_score < 0.7:
            return False

        # Check load balancing
        if model.current_load > 0.9:
            return False

        # Check health status (simplified)
        current_time = time.time()
        if current_time - model.last_health_check > 300:  # 5 minutes
            # Would perform actual health check here
            model.last_health_check = current_time

        return True

    def _score_candidates(
        self,
        candidates: List[ModelConfig],
        ir: PromptIR,
        strategy: RoutingStrategy,
        constraints: Dict[str, Any],
    ) -> List[Tuple[ModelConfig, float]]:
        """Score candidates based on routing strategy."""
        scored = []

        for model in candidates:
            score = 0.0

            if strategy == RoutingStrategy.TASK_BASED:
                score = self._score_task_based(model, ir)
            elif strategy == RoutingStrategy.COST_BASED:
                score = self._score_cost_based(model, ir)
            elif strategy == RoutingStrategy.PERFORMANCE_BASED:
                score = self._score_performance_based(model, ir)
            elif strategy == RoutingStrategy.AVAILABILITY_BASED:
                score = self._score_availability_based(model, ir)
            elif strategy == RoutingStrategy.HYBRID:
                score = self._score_hybrid(model, ir, constraints)

            scored.append((model, score))

        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _score_task_based(self, model: ModelConfig, ir: PromptIR) -> float:
        """Score model based on task compatibility."""
        score = 0.0

        # Intent-specialization matching
        intent_specialization_map = {
            IntentType.ANALYZE: ["analysis", "reasoning"],
            IntentType.GENERATE: ["generation", "creative_writing"],
            IntentType.CODE: ["coding", "debugging", "technical"],
            IntentType.SUMMARIZE: ["analysis", "general"],
            IntentType.TRANSLATE: ["general", "analysis"],
        }

        required_specializations = intent_specialization_map.get(ir.intent, [
                                                                 "general"])
        specialization_match = len(
            set(model.specializations) & set(required_specializations)
        )
        score += (specialization_match / len(required_specializations)) * 0.5

        # Capability matching
        complexity_score = {
            ModelCapability.BASIC: 0.3,
            ModelCapability.STANDARD: 0.6,
            ModelCapability.ADVANCED: 0.8,
            ModelCapability.SPECIALIZED: 1.0,
        }
        score += complexity_score.get(model.capability, 0.5) * 0.3

        # Reliability
        score += model.reliability_score * 0.2

        return score

    def _score_cost_based(self, model: ModelConfig, ir: PromptIR) -> float:
        """Score model based on cost efficiency."""
        # Lower cost = higher score
        if model.cost_per_1k_tokens == 0:
            cost_score = 1.0  # Free models get highest score
        else:
            # Normalize cost (assuming max cost of $0.02 per 1K tokens)
            cost_score = max(0, 1.0 - (model.cost_per_1k_tokens / 0.02))

        return cost_score

    def _score_performance_based(self, model: ModelConfig, ir: PromptIR) -> float:
        """Score model based on performance."""
        # Lower latency = higher score
        latency_score = max(
            0, 1.0 - (model.avg_latency_ms / 3000)
        )  # Normalize to 3s max

        # Higher reliability = higher score
        reliability_score = model.reliability_score

        # Higher capability = higher score
        capability_score = {
            ModelCapability.BASIC: 0.5,
            ModelCapability.STANDARD: 0.7,
            ModelCapability.ADVANCED: 0.9,
            ModelCapability.SPECIALIZED: 1.0,
        }.get(model.capability, 0.7)

        return (
            (latency_score * 0.4) + (reliability_score * 0.3) +
            (capability_score * 0.3)
        )

    def _score_availability_based(self, model: ModelConfig, ir: PromptIR) -> float:
        """Score model based on availability."""
        # Lower load = higher score
        load_score = max(0, 1.0 - model.current_load)

        # Higher reliability = higher score
        reliability_score = model.reliability_score

        return (load_score * 0.6) + (reliability_score * 0.4)

    def _score_hybrid(
        self, model: ModelConfig, ir: PromptIR, constraints: Dict[str, Any]
    ) -> float:
        """Score model using hybrid approach."""
        weights = self.routing_weights

        task_score = self._score_task_based(model, ir)
        cost_score = self._score_cost_based(model, ir)
        performance_score = self._score_performance_based(model, ir)
        availability_score = self._score_availability_based(model, ir)

        # Specialization bonus
        specialization_bonus = 0.0
        if ir.entity == EntityType.CODE and "coding" in model.specializations:
            specialization_bonus = 0.1
        elif ir.intent == IntentType.ANALYZE and "analysis" in model.specializations:
            specialization_bonus = 0.1

        total_score = (
            task_score * weights["task_match"]
            + cost_score * weights["cost_efficiency"]
            + performance_score * weights["performance"]
            + availability_score * weights["availability"]
            + specialization_bonus * weights["specialization"]
        )

        return total_score

    def _select_best_model(
        self,
        scored_candidates: List[Tuple[ModelConfig, float]],
        strategy: RoutingStrategy,
    ) -> Tuple[ModelConfig, float, str]:
        """Select best model from scored candidates."""
        if not scored_candidates:
            # Fallback to any available model
            fallback_model = list(self.model_registry.values())[0]
            return fallback_model, 0.5, "No suitable candidates found, using fallback"

        best_model, best_score = scored_candidates[0]

        # Generate reasoning
        reasoning = self._generate_reasoning(
            best_model, best_score, strategy, scored_candidates
        )

        return best_model, best_score, reasoning

    def _generate_reasoning(
        self,
        model: ModelConfig,
        score: float,
        strategy: RoutingStrategy,
        all_candidates: List[Tuple[ModelConfig, float]],
    ) -> str:
        """Generate reasoning for model selection."""
        reasons = []

        if strategy == RoutingStrategy.HYBRID:
            if model.cost_per_1k_tokens == 0:
                reasons.append("Cost-effective (free)")
            elif model.cost_per_1k_tokens < 0.001:
                reasons.append("Low cost")

            if model.avg_latency_ms < 1000:
                reasons.append("Fast response")

            if model.reliability_score > 0.95:
                reasons.append("High reliability")

            if model.capability in [
                ModelCapability.ADVANCED,
                ModelCapability.SPECIALIZED,
            ]:
                reasons.append("Advanced capabilities")

            if len(model.specializations) > 2:
                reasons.append(
                    f"Specialized in: {', '.join(model.specializations[:2])}"
                )

        confidence = "high" if score > 0.8 else "medium" if score > 0.6 else "low"

        reasoning_text = f"Selected for: {', '.join(reasons)}. Confidence: {confidence}"

        return reasoning_text

    def _get_alternatives(
        self,
        scored_candidates: List[Tuple[ModelConfig, float]],
        selected_model: ModelConfig,
    ) -> List[ModelConfig]:
        """Get alternative models."""
        alternatives = []

        for model, score in scored_candidates[1:4]:  # Top 3 alternatives
            if score > 0.3:  # Minimum score threshold
                alternatives.append(model)

        return alternatives

    def _estimate_cost(self, model: ModelConfig, ir: PromptIR) -> float:
        """Estimate cost for using model."""
        if not ir.token_estimate:
            return 0.0

        # Estimate input + output tokens (output typically ~1/3 of input)
        total_tokens = ir.token_estimate * 1.33

        return (total_tokens / 1000) * model.cost_per_1k_tokens

    def _estimate_latency(self, model: ModelConfig, ir: PromptIR) -> int:
        """Estimate latency for model."""
        base_latency = model.avg_latency_ms

        # Adjust based on token count (simplified)
        if ir.token_estimate:
            token_factor = min(ir.token_estimate / 1000,
                               2.0)  # Max 2x base latency
            return int(base_latency * token_factor)

        return base_latency

    def update_model_load(self, model_name: str, load_change: float):
        """Update model load for load balancing."""
        if model_name in self.model_registry:
            model = self.model_registry[model_name]
            model.current_load = max(
                0.0, min(1.0, model.current_load + load_change))

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total_models = len(self.model_registry)
        available_models = sum(
            1
            for model in self.model_registry.values()
            if self._is_model_available(model)
        )

        avg_cost = (
            sum(m.cost_per_1k_tokens for m in self.model_registry.values())
            / total_models
        )
        avg_latency = (
            sum(m.avg_latency_ms for m in self.model_registry.values()) / total_models
        )
        avg_reliability = (
            sum(m.reliability_score for m in self.model_registry.values())
            / total_models
        )

        return {
            "total_models": total_models,
            "available_models": available_models,
            "availability_rate": available_models / total_models,
            "avg_cost_per_1k": avg_cost,
            "avg_latency_ms": avg_latency,
            "avg_reliability": avg_reliability,
            "models_by_provider": {
                provider: len(
                    [m for m in self.model_registry.values() if m.provider ==
                     provider]
                )
                for provider in set(m.provider for m in self.model_registry.values())
            },
        }

    def _resolve_strategy(
        self,
        ir: PromptIR,
        strategy: RoutingStrategy | None,
        constraints: Dict[str, Any],
    ) -> RoutingStrategy:
        if strategy is not None:
            return strategy
        if constraints.get("force_local") or constraints.get("local_advisor"):
            return RoutingStrategy.LOCAL_PRIVACY
        if ir.requires_privacy_masking() and constraints.get("prefer_local"):
            return RoutingStrategy.LOCAL_PRIVACY
        return self.default_strategy

    def register_local_models(self, report) -> None:
        """Register PrivyFit recommendations into the model registry."""
        self._local_advisor_report = report
        for rec in report.top_models:
            key = rec.ollama_pull_name or rec.model_id.split("/")[-1]
            tags = report.workload.specialization_tags
            self.model_registry[key] = ModelConfig(
                name=key,
                provider="ollama",
                capability=ModelCapability.ADVANCED,
                cost_per_1k_tokens=0.0,
                avg_latency_ms=int(1000 / max(rec.estimated_tok_s or 5, 1)),
                max_tokens=max(report.workload.context_length_required, 8192),
                supports_streaming=True,
                reliability_score=rec.confidence,
                specializations=tags + ["privacy"],
            )

    def _route_local_privacy(
        self, ir: PromptIR, constraints: Dict[str, Any]
    ) -> Optional[RoutingDecision]:
        """Route to PrivyFit-recommended local model."""
        from ..local_advisor.advisor import recommend_local_model

        sample_prompts = constraints.get("sample_prompts") or [ir.original_prompt]
        mode = constraints.get("mode", "balanced")
        try:
            report = recommend_local_model(
                prompts=sample_prompts,
                mode=mode,
                top=constraints.get("local_top", 3),
                probe=constraints.get("probe", False),
            )
        except Exception:
            return None

        if not report.top_pick:
            return None

        self.register_local_models(report)
        pick = report.top_pick
        model_key = pick.ollama_pull_name or pick.model_id.split("/")[-1]
        selected = self.model_registry.get(model_key)
        if not selected:
            return None

        return RoutingDecision(
            selected_model=selected,
            routing_strategy=RoutingStrategy.LOCAL_PRIVACY,
            confidence_score=pick.confidence,
            reasoning=f"PrivyFit: {pick.reasoning}",
            alternative_models=[],
            estimated_cost=0.0,
            estimated_latency=selected.avg_latency_ms,
        )


class LoadBalancer:
    """Load balancer for model requests."""

    def __init__(self):
        self.request_counts = {}
        self.last_reset = time.time()

    def record_request(self, model_name: str):
        """Record a request to a model."""
        if model_name not in self.request_counts:
            self.request_counts[model_name] = 0
        self.request_counts[model_name] += 1

    def get_least_loaded_model(self, candidates: List[ModelConfig]) -> ModelConfig:
        """Get least loaded model from candidates."""
        return min(candidates, key=lambda m: m.current_load)

    def reset_counts(self):
        """Reset request counts (call periodically)."""
        current_time = time.time()
        if current_time - self.last_reset > 3600:  # Reset every hour
            self.request_counts.clear()
            self.last_reset = current_time
