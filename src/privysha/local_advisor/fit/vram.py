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

"""VRAM usage estimation."""

from __future__ import annotations

from ..constants import FRAMEWORK_OVERHEAD_BYTES
from ..types import GGUFVariant, ModelInfo
from .quantization import estimate_weight_bytes

_KV_BYTES_PER_BPARAM_PER_KCTX = 3.5 * 1024 * 1024
_MOE_ATTENTION_PARAM_MULTIPLIER = 4.0


def estimate_kv_cache(model: ModelInfo, context_length: int) -> int:
    if model.is_moe and model.parameter_count_active:
        active_b = model.parameter_count_active / 1e9
        params_b = active_b * _MOE_ATTENTION_PARAM_MULTIPLIER
    else:
        params_b = model.parameter_count / 1e9
    ctx_k = context_length / 1024
    return max(int(params_b * ctx_k * _KV_BYTES_PER_BPARAM_PER_KCTX), 0)


def _activation_bytes(model: ModelInfo, context_length: int) -> int:
    effective_p = (
        model.parameter_count_active
        if model.is_moe and model.parameter_count_active
        else model.parameter_count
    )
    base = 400_000_000
    param_term = int(effective_p * 0.08)
    ctx_term = int((context_length / 4096) * 150_000_000)
    return base + param_term + ctx_term


def estimate_vram(
    model: ModelInfo,
    variant: GGUFVariant | None,
    context_length: int = 4096,
) -> int:
    weights = estimate_weight_bytes(model, variant)
    kv_cache = estimate_kv_cache(model, context_length)
    activation = _activation_bytes(model, context_length)
    return weights + kv_cache + activation + FRAMEWORK_OVERHEAD_BYTES
