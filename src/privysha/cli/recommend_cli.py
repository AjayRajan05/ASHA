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

"""CLI for PrivyFit local model recommendations."""

from __future__ import annotations

import json
import sys
from typing import Optional

import click

from ..local_advisor.advisor import recommend_local_model


@click.command("recommend")
@click.option("--prompt", "-p", multiple=True, help="Sample prompt (repeatable)")
@click.option("--prompts", type=click.Path(exists=True), help="JSON/JSONL prompts file")
@click.option("--mode", "-m", default="balanced", help="Processing mode")
@click.option("--top", default=5, show_default=True, help="Number of recommendations")
@click.option("--gpu", help='Simulate GPU, e.g. "RTX 4090"')
@click.option("--vram", type=float, help="VRAM override in GB when simulating GPU")
@click.option("--cpu-only", is_flag=True, help="Rank for CPU-only inference")
@click.option("--refresh", is_flag=True, help="Refresh HuggingFace catalog cache")
@click.option("--probe", is_flag=True, help="Run optional Ollama micro-benchmark")
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def recommend_cmd(
    prompt: tuple[str, ...],
    prompts: Optional[str],
    mode: str,
    top: int,
    gpu: Optional[str],
    vram: Optional[float],
    cpu_only: bool,
    refresh: bool,
    probe: bool,
    as_json: bool,
) -> None:
    """Recommend local LLM models for your workload and hardware (PrivyFit)."""
    prompt_list = list(prompt) if prompt else None
    if not prompt_list and not prompts:
        click.echo("Provide --prompt or --prompts", err=True)
        sys.exit(1)

    try:
        report = recommend_local_model(
            prompts=prompt_list,
            prompts_file=prompts,
            mode=mode,
            top=top,
            gpu=gpu,
            vram_gb=vram,
            cpu_only=cpu_only,
            refresh_catalog=refresh,
            probe=probe,
        )
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(report.to_dict(), indent=2))
        return

    click.echo("\nPrivyFit — Local Model Recommendations")
    click.echo("=" * 50)
    click.echo(f"Catalog: {report.catalog_source} | Mode: {report.workload.mode}")
    click.echo(
        f"Workload: avg {report.workload.avg_compiled_tokens} compiled tokens, "
        f"PII rate {report.workload.pii_rate:.0%}, "
        f"local required: {report.workload.requires_local}"
    )
    if report.hardware.gpus:
        g = report.hardware.gpus[0]
        click.echo(f"Hardware: {g.name} ({g.vram_bytes // (1024**3)} GB VRAM)")
    else:
        click.echo(f"Hardware: CPU-only ({report.hardware.cpu_name})")

    if not report.top_models:
        click.echo("\nNo compatible models found for this workload/hardware.")
        return

    click.echo("")
    for i, rec in enumerate(report.top_models, 1):
        click.echo(
            f"#{i}  {rec.model_id}  {rec.quant}  "
            f"score {rec.scores.final_score:.1f}  "
            f"{rec.estimated_tok_s or '?'} tok/s  [{rec.fit_type}]"
        )
        click.echo(f"     {rec.reasoning}")
        if rec.ollama_pull_name:
            click.echo(f"     ollama: {rec.ollama_pull_name}")
