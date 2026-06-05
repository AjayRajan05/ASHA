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

"""
PrivySHA CLI - Demo and quick testing interface.

This is the BIGGEST adoption driver - lets developers try PrivySHA instantly.
"""

import click
import sys

from ..utils.dropin import process


@click.command()
@click.argument("prompt")
@click.option("--debug", "-d", is_flag=True, help="Show detailed metrics")
@click.option(
    "--mode", "-m", default="balanced", help="Processing mode (balanced/strict/lite)"
)
@click.option(
    "--stages", "-s", is_flag=True, help="Use enhanced stage-based processing"
)
@click.option("--context", "-c", help="Context configuration (JSON format)")
@click.option(
    "--debug-mode",
    is_flag=True,
    help="Enable comprehensive debugging with PrivySHADebugger",
)
def demo(
    prompt: str, debug: bool, mode: str, stages: bool, context: str, debug_mode: bool
) -> None:
    """
    Demo PrivySHA with any prompt.

    This is the viral adoption driver - shows instant value.

    Example:
        privysha "My email is john@gmail.com. Analyze this dataset."

        privysha -d "Contact me at 555-1234 for help with the API key abc123"

        privysha -s -c '{"role": "data scientist"}' "Analyze customer data"
    """
    try:
        # Parse context configuration if provided
        context_config = None
        if context:
            import json

            context_config = json.loads(context)

        # Map mode to security level
        security_level = {"balanced": "medium", "strict": "high", "lite": "low"}.get(
            mode, "medium"
        )

        # Process the prompt with enhanced features
        result = process(
            prompt,
            return_metrics=True,
            debug=debug,
            security_level=security_level,
            use_stages=stages,
            context_config=context_config,
            debug_mode=debug_mode,
        )

        # Display results
        print("\n" + "=" * 60)
        print("PrivySHA Enhanced Demo - Full Library Integration")
        print("=" * 60)

        print(f"\nOriginal Prompt:")
        print(f"   {prompt}")

        print(f"\nProcessed Prompt:")
        print(f"   {result['optimized']}")

        # Show configuration used
        print(f"\nConfiguration:")
        print(f"   Mode: {mode}")
        print(f"   Stages: {'Enabled' if stages else 'Disabled'}")
        print(f"   Context: {'Applied' if context_config else 'None'}")
        print(f"   Debug Mode: {'Enabled' if debug_mode else 'Disabled'}")

        # Show metrics
        print(f"\nResults:")
        print(f"   Tokens Saved: {result.get('token_reduction', 0)}%")
        print(
            f"   PII Detected: {len(result.get('security_result', {}).get('masked_entities', []))} items"
        )

        if debug:
            # Show detailed metrics
            metrics = result.get("metrics", {})
            print(f"\nDetailed Metrics:")
            print(f"   Cost Reduction: {metrics.get('cost_reduction', '0%')}")
            print(f"   Risk Level: {metrics.get('risk_level', 'unknown')}")
            print(f"   Threats Blocked: {metrics.get('threats_blocked', 0)}")

        if debug_mode and "comprehensive_debug" in result:
            # Show comprehensive debug information
            debug_info = result["comprehensive_debug"]
            print(f"\nComprehensive Debug:")
            print(f"   Session ID: {debug_info.get('session_id', 'unknown')}")
            print(
                f"   Total Execution Time: {debug_info.get('total_execution_time_ms', 0):.1f}ms"
            )
            print(f"   Stages Executed: {len(debug_info.get('stages', []))}")

            if debug_info.get("stages"):
                print(f"\nStage Details:")
                for stage in debug_info["stages"]:
                    print(
                        f"   - {stage['stage_name']}: {stage['execution_time_ms']:.1f}ms (Success: {stage['success']})"
                    )
            print(
                f"   Processing Time: {metrics.get('processing_time_ms', 0)}ms")

            # Show security details
            security = result.get("security_result", {})
            print(f"\nSecurity Details:")
            print(f"   Threats Blocked: {security.get('threats_detected', 0)}")
            print(f"   PII Types: {metrics.get('pii_detected', [])}")

        # Show change summary
        if result["optimized"] != prompt:
            print(f"\nSummary: Prompt optimized and secured successfully!")
        else:
            print(f"\nSummary: Prompt was already safe and optimal")

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"\nError: {str(e)}")
        print('Try: privysha "simple test prompt"')
        sys.exit(1)


@click.command()
def quick_test() -> None:
    """
    Run quick built-in tests to verify PrivySHA works.
    """
    print("\nPrivySHA Quick Test Suite")
    print("=" * 40)

    test_cases = [
        {
            "name": "Basic PII Detection",
            "prompt": "My email is john@gmail.com",
            "should_mask": True,
        },
        {
            "name": "Safe Prompt (No Change)",
            "prompt": "Hello, summarize this text",
            "should_mask": False,
        },
        {
            "name": "Multiple PII Types",
            "prompt": "Call me at 555-1234 or email john@company.com",
            "should_mask": True,
        },
    ]

    passed = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Input: {test['prompt']}")

        try:
            result = process(test["prompt"], return_metrics=True)
            pii_masked = result.get("pii_masked", False)

            if pii_masked == test["should_mask"]:
                print(f"PASS - PII masked: {pii_masked}")
                passed += 1
            else:
                print(
                    f"FAIL - Expected PII masked: {test['should_mask']}, got: {pii_masked}"
                )

        except Exception as e:
            print(f"ERROR - {str(e)}")

    print(f"\n{'='*40}")
    print(f" Results: {passed}/{total} tests passed")

    if passed == total:
        print(" All tests passed! PrivySHA is working correctly.")
    else:
        print("Some tests failed. Check your installation.")

    print("=" * 40)


@click.command()
@click.option("--count", "-n", default=5, help="Number of example prompts")
def examples(count: int) -> None:
    """
    Show example prompts and their results.
    """
    examples = [
        "My email is john@gmail.com. Analyze this dataset.",
        "Call me at 555-1234 for help with API key abc123.",
        "Contact Jane Smith at jane@company.com for the project.",
        "The user's IP is 192.168.1.1 and email is admin@site.com.",
        "Hello, can you help me with this simple question?",
    ]

    print(f"\nPrivySHA Examples (showing first {min(count, len(examples))})")
    print("=" * 60)

    for i, example in enumerate(examples[:count], 1):
        print(f"\n{i}. {example}")

        try:
            result = process(example, return_metrics=True)
            print(f"{result['optimized']}")
            print(
                f"Saved: {result.get('token_reduction', 0)}% | PII: {result.get('pii_masked', False)}"
            )
        except Exception as e:
            print(f"Error: {str(e)}")

    print("\n" + "=" * 60)
    print('💡 Try: privysha "your own prompt here"')


@click.group()
def cli() -> None:
    """PrivySHA CLI - Drop-in security and optimization for LLM apps."""


# Add commands
cli.add_command(demo)
cli.add_command(quick_test)
cli.add_command(examples)

# Add benchmark command
try:
    from .benchmark_cli import run_benchmark

    @click.command()
    @click.option("--mode", "-m", default="balanced", help="Policy mode to test")
    @click.option("--config", "-c", help="Use preset configuration")
    @click.option("--custom", help="Test custom prompt")
    @click.option("--compare", help="Compare with previous results")
    @click.option("--output", "-o", help="Output directory")
    @click.option("--save", "-s", is_flag=True, help="Save results")
    @click.option("--format", "-f", default="readable", help="Output format")
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    @click.option("--quiet", "-q", is_flag=True, help="Quiet mode")
    @click.option("--timeout", default=5000, help="Timeout per test (ms)")
    def benchmark(
        mode: str,
        config: str,
        custom: str,
        compare: str,
        output: str,
        save: bool,
        format: str,
        verbose: bool,
        quiet: bool,
        timeout: int,
    ) -> None:
        """Run comprehensive benchmarks."""

        # Create args object for benchmark function
        class Args:
            def __init__(self):
                self.mode = mode
                self.config = config
                self.custom = custom
                self.compare = compare
                self.output = output
                self.save = save
                self.format = format
                self.verbose = verbose
                self.quiet = quiet
                self.timeout = timeout

        return run_benchmark(Args())

    cli.add_command(benchmark)
except ImportError:
    # Benchmark CLI not available
    pass

try:
    from .recommend_cli import recommend_cmd

    cli.add_command(recommend_cmd)
except ImportError:
    pass


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    cli()
