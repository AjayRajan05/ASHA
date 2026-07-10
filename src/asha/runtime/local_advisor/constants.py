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

"""Hardware and quantization constants for AshaFit fit engine."""

_GiB = 1024**3

FRAMEWORK_OVERHEAD_BYTES = 500_000_000
MIN_COMPUTE_CAPABILITY_OLLAMA = (5, 0)

QUANT_BYTES_PER_WEIGHT = {
    "F32": 4.0,
    "F16": 2.0,
    "BF16": 2.0,
    "Q8_0": 1.0625,
    "Q6_K": 0.8125,
    "Q5_K_M": 0.6875,
    "Q5_K_S": 0.6875,
    "Q5_0": 0.625,
    "Q4_K_M": 0.5625,
    "Q4_K_S": 0.5625,
    "Q4_0": 0.5,
    "Q3_K_M": 0.4375,
    "Q3_K_S": 0.4375,
    "Q2_K": 0.3125,
}

QUANT_QUALITY_PENALTY = {
    "Q8_0": 0.01,
    "Q6_K": 0.02,
    "Q5_K_M": 0.03,
    "Q4_K_M": 0.05,
    "Q4_0": 0.06,
    "Q3_K_M": 0.08,
    "Q2_K": 0.25,
}

QUANT_PREFERENCE_ORDER = [
    "Q8_0",
    "Q6_K",
    "Q5_K_M",
    "Q4_K_M",
    "Q4_0",
    "Q3_K_M",
    "Q2_K",
]

FIT_MULTIPLIERS = {
    "full_gpu": 1.0,
    "partial_offload": 0.72,
    "cpu_only": 0.5,
}

MIN_SPEED_TOK_S = {
    "full_gpu": 8.0,
    "partial_offload": 4.0,
    "cpu_only": 1.5,
}

GPU_BANDWIDTH = {
    "RTX 5090": 1792.0,
    "RTX 4090": 1008.0,
    "RTX 4080": 716.8,
    "RTX 4070": 504.0,
    "RTX 4060": 272.0,
    "RTX 3090": 936.2,
    "RTX 3080": 760.3,
    "RTX 3060": 360.0,
    "APPLE M4 MAX": 546.0,
    "APPLE M3 MAX": 400.0,
    "APPLE M2 MAX": 400.0,
    "APPLE M1 MAX": 400.0,
    "RADEON 780M": 256.0,
}

AMD_APU_MARKERS = (
    "RADEON 780M",
    "RADEON 890M",
    "RYZEN AI",
)

CACHE_TTL_SECONDS = 6 * 3600
