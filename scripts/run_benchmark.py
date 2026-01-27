#!/usr/bin/env python3
"""
Benchmark script for comparing TVM and OpenXLA compilation.

This script runs comprehensive benchmarks on both compilers across
different platforms and generates performance reports.
"""

import argparse
import sys
from pathlib import Path
import json
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.tvm_compiler import TVMCompiler
from app.services.xla_compiler import XLACompiler
from app.services.model_exporter import ModelExporter
from app.utils.performance import PerformanceMonitor
from app.models.schemas import CompilerType, TargetPlatform, ModelType, ExportFormat
import torch.nn as nn
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Run comprehensive benchmarks."""

    def __init__(self):
        """Initialize benchmark runner."""
        self.monitor = PerformanceMonitor()
        self.results = {}

    def create_test_model(self, model_type: ModelType) -> nn.Module:
        """Create a test model."""
        if model_type == ModelType.LLM:

            class TestLLM(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.embedding = nn.Embedding(1000, 128)
                    self.lstm = nn.LSTM(128, 256, batch_first=True)
                    self.fc = nn.Linear(256, 1000)

                def forward(self, x):
                    x = self.embedding(x)
                    x, _ = self.lstm(x)
                    x = self.fc(x)
                    return x

            return TestLLM()

        elif model_type == ModelType.KEYWORD_SPOTTING:

            class TestKWS(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.conv1 = nn.Conv1d(40, 64, 3, padding=1)
                    self.conv2 = nn.Conv1d(64, 128, 3, padding=1)
                    self.pool = nn.AdaptiveAvgPool1d(1)
                    self.fc = nn.Linear(128, 10)

                def forward(self, x):
                    x = torch.relu(self.conv1(x))
                    x = torch.relu(self.conv2(x))
                    x = self.pool(x).squeeze(-1)
                    x = self.fc(x)
                    return x

            return TestKWS()

    def run_benchmark(
        self,
        model_name: str,
        model_type: ModelType,
        compilers: list,
        platforms: list,
    ):
        """
        Run benchmark for a model across compilers and platforms.

        Args:
            model_name: Name of the model
            model_type: Type of the model
            compilers: List of compilers to test
            platforms: List of platforms to test
        """
        logger.info(f"Starting benchmark for {model_name}")

        # Create test model
        model = self.create_test_model(model_type)
        exporter = ModelExporter()

        # Export to different formats
        logger.info("Exporting model...")
        onnx_result = exporter.export_model(
            model=model,
            model_name=model_name,
            model_type=model_type,
            export_format=ExportFormat.ONNX,
        )

        torchscript_result = exporter.export_model(
            model=model,
            model_name=model_name,
            model_type=model_type,
            export_format=ExportFormat.TORCHSCRIPT,
        )

        # Run benchmarks for each compiler and platform
        for compiler in compilers:
            for platform in platforms:
                key = f"{compiler.value}_{platform.value}"
                logger.info(f"Benchmarking {key}...")

                try:
                    if compiler == CompilerType.TVM:
                        self._benchmark_tvm(
                            onnx_result["output_path"],
                            model_name,
                            platform,
                            key,
                        )
                    elif compiler == CompilerType.OPENXLA:
                        self._benchmark_xla(
                            torchscript_result["output_path"],
                            model_name,
                            platform,
                            key,
                        )
                except Exception as e:
                    logger.error(f"Benchmark failed for {key}: {e}")
                    self.results[key] = {"error": str(e)}

        # Generate comparison report
        self._generate_report(model_name, model_type)

    def _benchmark_tvm(
        self, model_path: str, model_name: str, platform: TargetPlatform, key: str
    ):
        """Benchmark TVM compilation."""
        compiler = TVMCompiler()

        with self.monitor.measure(f"{key}_compilation"):
            result = compiler.compile_model(
                model_path=model_path,
                model_name=model_name,
                target_platform=platform,
            )

        self.results[key] = result

    def _benchmark_xla(
        self, model_path: str, model_name: str, platform: TargetPlatform, key: str
    ):
        """Benchmark XLA compilation."""
        compiler = XLACompiler()

        with self.monitor.measure(f"{key}_compilation"):
            result = compiler.compile_model(
                model_path=model_path,
                model_name=model_name,
                target_platform=platform,
            )

        self.results[key] = result

    def _generate_report(self, model_name: str, model_type: ModelType):
        """Generate benchmark report."""
        report = {
            "model_name": model_name,
            "model_type": model_type.value,
            "results": self.results,
            "metrics_history": self.monitor.metrics_history,
        }

        # Save report
        output_path = f"benchmark_report_{model_name}.json"
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Benchmark report saved to {output_path}")

        # Print summary
        print("\n" + "=" * 80)
        print(f"BENCHMARK SUMMARY: {model_name}")
        print("=" * 80)
        for key, result in self.results.items():
            if "error" in result:
                print(f"\n{key}: FAILED - {result['error']}")
            else:
                print(f"\n{key}:")
                print(f"  Compilation Time: {result.get('compilation_time_s', 0):.2f}s")
                print(f"  Binary Path: {result.get('binary_path', 'N/A')}")
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run model compilation benchmarks")
    parser.add_argument(
        "--model-name", default="benchmark_model", help="Name of the model"
    )
    parser.add_argument(
        "--model-type",
        choices=["llm", "keyword_spotting"],
        default="llm",
        help="Type of model",
    )
    parser.add_argument(
        "--compilers",
        nargs="+",
        choices=["tvm", "openxla"],
        default=["tvm", "openxla"],
        help="Compilers to benchmark",
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["x86", "arm"],
        default=["x86"],
        help="Platforms to benchmark",
    )

    args = parser.parse_args()

    # Convert arguments
    model_type = ModelType(args.model_type)
    compilers = [CompilerType(c) for c in args.compilers]
    platforms = [TargetPlatform(p) for p in args.platforms]

    # Run benchmark
    runner = BenchmarkRunner()
    runner.run_benchmark(
        model_name=args.model_name,
        model_type=model_type,
        compilers=compilers,
        platforms=platforms,
    )


if __name__ == "__main__":
    main()
