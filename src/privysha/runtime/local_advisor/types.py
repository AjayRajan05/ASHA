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

"""PrivyFit data types for project-aware local LLM recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...core._ir.prompt_ir import IntentType


@dataclass
class WorkloadProfile:
    """Aggregated workload fingerprint from compiled prompt corpus."""

    intent_distribution: Dict[str, float]
    avg_compiled_tokens: int
    p95_compiled_tokens: int
    max_compiled_tokens: int
    avg_complexity: float
    pii_rate: float
    requires_local: bool
    dominant_intents: List[IntentType]
    context_length_required: int
    specialization_tags: List[str]
    sample_compiled_prompts: List[str] = field(default_factory=list)
    mode: str = "balanced"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_distribution": self.intent_distribution,
            "avg_compiled_tokens": self.avg_compiled_tokens,
            "p95_compiled_tokens": self.p95_compiled_tokens,
            "max_compiled_tokens": self.max_compiled_tokens,
            "avg_complexity": self.avg_complexity,
            "pii_rate": self.pii_rate,
            "requires_local": self.requires_local,
            "dominant_intents": [i.value for i in self.dominant_intents],
            "context_length_required": self.context_length_required,
            "specialization_tags": self.specialization_tags,
            "mode": self.mode,
        }


@dataclass
class GPUInfo:
    name: str
    vendor: str
    vram_bytes: int
    compute_capability: Optional[tuple[int, int]] = None
    memory_bandwidth_gbps: Optional[float] = None
    shared_memory: bool = False


@dataclass
class HardwareProfile:
    gpus: List[GPUInfo] = field(default_factory=list)
    cpu_name: str = "Unknown"
    cpu_cores: int = 0
    has_avx2: bool = False
    ram_bytes: int = 0
    disk_free_bytes: int = 0
    os: str = "linux"
    backend_hint: str = "gguf"
    simulated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gpus": [
                {
                    "name": g.name,
                    "vendor": g.vendor,
                    "vram_bytes": g.vram_bytes,
                    "memory_bandwidth_gbps": g.memory_bandwidth_gbps,
                    "shared_memory": g.shared_memory,
                }
                for g in self.gpus
            ],
            "cpu_name": self.cpu_name,
            "cpu_cores": self.cpu_cores,
            "ram_bytes": self.ram_bytes,
            "disk_free_bytes": self.disk_free_bytes,
            "os": self.os,
            "backend_hint": self.backend_hint,
            "simulated": self.simulated,
        }


@dataclass
class GGUFVariant:
    filename: str
    quant_type: str
    file_size_bytes: int


@dataclass
class ModelInfo:
    id: str
    family_id: str
    name: str
    parameter_count: int
    parameter_count_active: Optional[int] = None
    architecture: str = ""
    is_moe: bool = False
    context_length: Optional[int] = None
    downloads: int = 0
    likes: int = 0
    gguf_variants: List[GGUFVariant] = field(default_factory=list)
    specialization_tags: List[str] = field(default_factory=list)
    instruction_following_score: float = 0.7
    ollama_name: Optional[str] = None


@dataclass
class CompatibilityResult:
    model: ModelInfo
    gguf_variant: Optional[GGUFVariant]
    can_run: bool
    vram_required_bytes: int
    vram_available_bytes: int
    fit_type: str
    warnings: List[str] = field(default_factory=list)
    context_fits: bool = True
    estimated_tok_per_sec: Optional[float] = None


@dataclass
class ScoreBreakdown:
    hardware_fit: float
    workload_fit: float
    privacy_compliance: float
    speed_usability: float
    final_score: float
    quant_penalty: float = 0.0


@dataclass
class ModelRecommendation:
    model_id: str
    quant: str
    fit_type: str
    estimated_tok_s: Optional[float]
    scores: ScoreBreakdown
    reasoning: str
    confidence: float
    ollama_pull_name: Optional[str] = None
    vram_required_gb: Optional[float] = None
    measured_tok_s: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "quant": self.quant,
            "fit_type": self.fit_type,
            "estimated_tok_s": self.estimated_tok_s,
            "measured_tok_s": self.measured_tok_s,
            "scores": {
                "hardware_fit": self.scores.hardware_fit,
                "workload_fit": self.scores.workload_fit,
                "privacy_compliance": self.scores.privacy_compliance,
                "speed_usability": self.scores.speed_usability,
                "final_score": self.scores.final_score,
            },
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "ollama_pull_name": self.ollama_pull_name,
            "vram_required_gb": self.vram_required_gb,
        }


@dataclass
class RecommendationReport:
    top_models: List[ModelRecommendation]
    workload: WorkloadProfile
    hardware: HardwareProfile
    catalog_source: str
    probed: bool = False

    @property
    def top_pick(self) -> Optional[ModelRecommendation]:
        return self.top_models[0] if self.top_models else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "top_models": [m.to_dict() for m in self.top_models],
            "top_pick": self.top_pick.to_dict() if self.top_pick else None,
            "workload": self.workload.to_dict(),
            "hardware": self.hardware.to_dict(),
            "catalog_source": self.catalog_source,
            "probed": self.probed,
        }
