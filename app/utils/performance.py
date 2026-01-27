"""
Performance monitoring and benchmarking utilities.

This module provides utilities for measuring and comparing performance
metrics across different compilers and platforms.
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Callable
from contextlib import contextmanager
import json
from pathlib import Path

from app.models.schemas import CompilerType, TargetPlatform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics_history = []

    @contextmanager
    def measure(self, operation_name: str):
        """
        Context manager to measure execution time and memory usage.

        Args:
            operation_name: Name of the operation being measured

        Yields:
            Dict containing metrics
        """
        process = psutil.Process()
        start_time = time.time()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        metrics = {"operation": operation_name}

        try:
            yield metrics
        finally:
            end_time = time.time()
            mem_after = process.memory_info().rss / 1024 / 1024  # MB

            metrics.update(
                {
                    "duration_s": end_time - start_time,
                    "memory_usage_mb": mem_after - mem_before,
                    "timestamp": time.time(),
                }
            )

            self.metrics_history.append(metrics)
            logger.info(
                f"{operation_name}: {metrics['duration_s']:.2f}s, "
                f"Memory: {metrics['memory_usage_mb']:.2f}MB"
            )

    def benchmark_inference(
        self,
        inference_func: Callable,
        input_data: Any,
        num_iterations: int = 100,
        warmup_iterations: int = 10,
    ) -> Dict[str, Any]:
        """
        Benchmark inference performance.

        Args:
            inference_func: Function to run inference
            input_data: Input data for inference
            num_iterations: Number of benchmark iterations
            warmup_iterations: Number of warm-up iterations

        Returns:
            Dict containing benchmark results
        """
        logger.info(f"Running {warmup_iterations} warm-up iterations")
        for _ in range(warmup_iterations):
            inference_func(input_data)

        logger.info(f"Running {num_iterations} benchmark iterations")
        latencies = []
        process = psutil.Process()

        for _ in range(num_iterations):
            start_time = time.time()
            inference_func(input_data)
            latency = (time.time() - start_time) * 1000  # ms
            latencies.append(latency)

        mem_info = process.memory_info()

        return {
            "num_iterations": num_iterations,
            "mean_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "p50_latency_ms": sorted(latencies)[len(latencies) // 2],
            "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)],
            "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)],
            "throughput_qps": 1000 / (sum(latencies) / len(latencies)),
            "memory_usage_mb": mem_info.rss / 1024 / 1024,
        }

    def compare_compilers(
        self,
        model_name: str,
        results: Dict[CompilerType, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Compare performance across different compilers.

        Args:
            model_name: Name of the model
            results: Results from different compilers

        Returns:
            Comparison analysis
        """
        comparison = {
            "model_name": model_name,
            "compilers": {},
            "analysis": {},
        }

        for compiler, metrics in results.items():
            comparison["compilers"][compiler.value] = metrics

        # Analyze results
        if len(results) > 1:
            latencies = {c: m["mean_latency_ms"] for c, m in results.items()}
            fastest = min(latencies, key=latencies.get)
            slowest = max(latencies, key=latencies.get)

            comparison["analysis"] = {
                "fastest_compiler": fastest.value,
                "slowest_compiler": slowest.value,
                "speedup": latencies[slowest] / latencies[fastest],
            }

        return comparison

    def save_metrics(self, output_path: str):
        """
        Save metrics history to file.

        Args:
            output_path: Path to save metrics
        """
        with open(output_path, "w") as f:
            json.dump(self.metrics_history, f, indent=2)
        logger.info(f"Metrics saved to {output_path}")

    def generate_report(
        self,
        model_name: str,
        compiler: CompilerType,
        platform: TargetPlatform,
        compilation_metrics: Dict[str, Any],
        inference_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Args:
            model_name: Name of the model
            compiler: Compiler used
            platform: Target platform
            compilation_metrics: Compilation performance metrics
            inference_metrics: Inference performance metrics

        Returns:
            Performance report
        """
        report = {
            "model_name": model_name,
            "compiler": compiler.value,
            "target_platform": platform.value,
            "compilation": {
                "time_s": compilation_metrics.get("compilation_time_s", 0),
                "optimizations": compilation_metrics.get("optimizations", {}),
            },
            "inference": {
                "mean_latency_ms": inference_metrics.get("mean_latency_ms", 0),
                "p95_latency_ms": inference_metrics.get("p95_latency_ms", 0),
                "p99_latency_ms": inference_metrics.get("p99_latency_ms", 0),
                "throughput_qps": inference_metrics.get("throughput_qps", 0),
                "memory_usage_mb": inference_metrics.get("memory_usage_mb", 0),
            },
            "cross_platform_consistency": self._check_consistency(
                model_name, compiler, platform
            ),
        }

        return report

    def _check_consistency(
        self, model_name: str, compiler: CompilerType, platform: TargetPlatform
    ) -> Dict[str, Any]:
        """
        Check cross-platform consistency.

        Args:
            model_name: Model name
            compiler: Compiler type
            platform: Platform type

        Returns:
            Consistency metrics
        """
        # Placeholder for consistency checking logic
        # In production, this would compare outputs across platforms
        return {
            "status": "not_implemented",
            "note": "Cross-platform consistency checking requires multi-device setup",
        }
