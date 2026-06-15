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

"""Quantization helpers for VRAM and speed estimation."""

from __future__ import annotations

import re

from ..constants import QUANT_QUALITY_PENALTY
from ..types import GGUFVariant, ModelInfo

_NON_GGUF_BYTES = {"AWQ": 0.5, "GPTQ": 0.5, "FP16": 2.0, "BF16": 2.0}


def infer_non_gguf_quant(model_id: str) -> str:
    lower = model_id.lower()
    if "awq" in lower:
        return "AWQ"
    if "gptq" in lower:
        return "GPTQ"
    if "bf16" in lower:
        return "BF16"
    return "FP16"


def effective_quant_type(model: ModelInfo, variant: GGUFVariant | None) -> str:
    if variant:
        return variant.quant_type.upper()
    return infer_non_gguf_quant(model.id)


def estimate_weight_bytes(model: ModelInfo, variant: GGUFVariant | None) -> int:
    if variant:
        return variant.file_size_bytes
    quant = infer_non_gguf_quant(model.id)
    bpw = _NON_GGUF_BYTES.get(quant, 2.0)
    return int(model.parameter_count * bpw)


def quant_quality_penalty(model: ModelInfo, variant: GGUFVariant | None) -> float:
    quant = effective_quant_type(model, variant).upper()
    return QUANT_QUALITY_PENALTY.get(quant, 0.05 if quant.startswith("Q") else 0.0)


def extract_quant_type(filename: str) -> str:
    upper = filename.upper()
    patterns = [
        r"[.-](Q\d+_K_[SMLA])",
        r"[.-](Q\d+_\d+)",
        r"[.-](Q\d+_K)",
        r"[.-](F16|FP16|BF16|F32)",
    ]
    for pattern in patterns:
        m = re.search(pattern, upper)
        if m:
            return m.group(1)
    return "Q4_K_M"
