"""Performance and scalability tests (slow marker)."""

import concurrent.futures

import pytest

from privysha.core.benchmark import BenchmarkHarness
from privysha.utils.dropin import process


@pytest.mark.slow
def test_large_prompt_under_budget():
    prompt = "Analyze this dataset. " * 500 + "Contact user@example.com"
    result = process(prompt, return_metrics=True)
    latency = result.get("performance_metrics", {}).get("total_pipeline_ms", 0)
    assert latency < 30000  # 30s budget for 10k+ chars


@pytest.mark.slow
def test_concurrent_process():
    prompts = [f"Email user{i}@test.com analyze data" for i in range(10)]

    def run_one(p):
        return process(p, return_metrics=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(run_one, prompts))

    assert len(results) == 10
    for r in results:
        assert "metrics" in r
        assert "user" not in r["optimized"] or "@" not in r["optimized"]


@pytest.mark.slow
def test_batch_throughput():
    prompts = [f"Summarize report {i}" for i in range(50)]
    for p in prompts:
        out = process(p)
        assert isinstance(out, str)


@pytest.mark.slow
def test_p95_latency_smoke():
    harness = BenchmarkHarness()
    harness.add_custom_test("p95_smoke", "Analyze sales data for Q1", expected_pii=0)
    summary = harness.run_benchmark()
    assert summary.avg_latency_ms < 10000
    assert summary.p95_latency_ms >= 0
