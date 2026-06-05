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

"""Tests for PrivyFit local model advisor."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from privysha.local_advisor.catalog.fetcher import load_fallback_catalog
from privysha.local_advisor.hardware_profiler import detect_hardware
from privysha.local_advisor.ranker import rank_models
from privysha.local_advisor.types import GPUInfo, HardwareProfile
from privysha.local_advisor.workload_profiler import load_prompts, profile_workload


SAMPLE_PROMPTS = [
    "Create a Python function that validates email addresses.",
    "My email is john@company.com — analyze this dataset.",
]


def test_load_prompts_from_json_file(tmp_path):
    path = tmp_path / "prompts.json"
    path.write_text(
        '[{"prompt": "Hello world"}, {"prompt": "Analyze data"}]',
        encoding="utf-8",
    )
    loaded = load_prompts(prompts_file=str(path))
    assert len(loaded) == 2
    assert "Hello world" in loaded[0]


def test_profile_workload_compiled_tokens():
    profile = profile_workload(SAMPLE_PROMPTS, mode="balanced")
    assert profile.avg_compiled_tokens > 0
    assert profile.context_length_required >= profile.p95_compiled_tokens
    assert profile.pii_rate > 0
    assert profile.requires_local is True
    assert "coding" in profile.specialization_tags or "analysis" in profile.specialization_tags


def test_rank_models_privacy_and_coding():
    workload = profile_workload(
        ["Write a Python API client for REST endpoints."],
        mode="strict",
    )
    hardware = detect_hardware(gpu="RTX 4090", vram_gb=24)
    catalog = load_fallback_catalog()
    ranked = rank_models(catalog, hardware, workload, top=3)
    assert ranked
    assert all(r.scores.final_score > 0 for r in ranked)
    assert ranked[0].ollama_pull_name


def test_rank_models_respects_vram_simulation():
    workload = profile_workload(["Summarize this paragraph."], mode="lite")
    small_gpu = HardwareProfile(
        gpus=[GPUInfo(name="RTX 4060", vendor="nvidia", vram_bytes=8 * 1024**3)],
        ram_bytes=16 * 1024**3,
        disk_free_bytes=100 * 1024**3,
    )
    large_gpu = detect_hardware(gpu="RTX 4090", vram_gb=24)
    catalog = load_fallback_catalog()
    small_ranked = rank_models(catalog, small_gpu, workload, top=5)
    large_ranked = rank_models(catalog, large_gpu, workload, top=5)
    assert small_ranked
    assert large_ranked
    small_max_params = max(
        next(m.parameter_count for m in catalog if m.id == r.model_id)
        for r in small_ranked
    )
    large_max_params = max(
        next(m.parameter_count for m in catalog if m.id == r.model_id)
        for r in large_ranked
    )
    assert large_max_params >= small_max_params


@patch("privysha.local_advisor.catalog.fetcher.fetch_live_catalog")
def test_recommend_local_model_uses_fallback(mock_fetch):
    mock_fetch.side_effect = RuntimeError("offline")
    from privysha import recommend_local_model

    report = recommend_local_model(
        prompts=SAMPLE_PROMPTS,
        mode="balanced",
        gpu="RTX 4090",
        refresh_catalog=True,
        top=2,
    )
    assert report.catalog_source == "fallback"
    assert len(report.top_models) <= 2
    assert report.workload.requires_local


def test_recommend_report_json_serializable():
    from privysha import recommend_local_model
    import json

    report = recommend_local_model(
        prompts=SAMPLE_PROMPTS,
        mode="balanced",
        gpu="RTX 4090",
        top=1,
    )
    payload = json.dumps(report.to_dict())
    data = json.loads(payload)
    assert "top_models" in data
    assert data.get("top_pick") or data["top_models"]
