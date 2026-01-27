"""
Inference API endpoints.

This module provides REST API endpoints for running inference
using compiled models.
"""

from fastapi import APIRouter, HTTPException
import numpy as np
import torch
import logging
from typing import Dict, Any

from app.models.schemas import (
    InferenceRequest,
    InferenceResponse,
    CompilerType,
    TargetPlatform,
)
from app.services.tvm_compiler import TVMCompiler
from app.services.xla_compiler import XLACompiler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/inference/tvm", response_model=InferenceResponse)
async def run_tvm_inference(request: InferenceRequest):
    """
    Run inference using a TVM-compiled model.

    Args:
        request: Inference request with binary path and input data

    Returns:
        Inference results with performance metrics
    """
    try:
        compiler = TVMCompiler()

        # Parse input data
        input_array = np.array(request.input_data["input"], dtype=np.float32)

        # Determine target platform from binary path
        if "_x86_" in request.binary_path:
            target_platform = TargetPlatform.X86
        elif "_arm_" in request.binary_path:
            target_platform = TargetPlatform.ARM
        else:
            target_platform = TargetPlatform.X86  # default

        # Run inference
        result = compiler.run_inference(
            binary_path=request.binary_path,
            target_platform=target_platform,
            input_data=input_array,
        )

        return InferenceResponse(
            predictions=result["output"],
            latency_ms=result["latency_ms"],
            memory_usage_mb=result["memory_usage_mb"],
            throughput=result["throughput"],
        )

    except Exception as e:
        logger.error(f"TVM inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inference/xla", response_model=InferenceResponse)
async def run_xla_inference(request: InferenceRequest):
    """
    Run inference using an XLA-compiled model.

    Args:
        request: Inference request with binary path and input data

    Returns:
        Inference results with performance metrics
    """
    try:
        compiler = XLACompiler()

        # Parse input data
        input_tensor = torch.tensor(
            request.input_data["input"], dtype=torch.float32
        )

        # Run inference
        result = compiler.run_inference(
            binary_path=request.binary_path,
            input_data=input_tensor,
        )

        return InferenceResponse(
            predictions=result["output"],
            latency_ms=result["latency_ms"],
            memory_usage_mb=result["memory_usage_mb"],
            throughput=result["throughput"],
        )

    except Exception as e:
        logger.error(f"XLA inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inference/benchmark")
async def benchmark_inference(
    binary_path: str,
    compiler: CompilerType,
    target_platform: TargetPlatform,
    num_iterations: int = 100,
) -> Dict[str, Any]:
    """
    Benchmark inference performance.

    Args:
        binary_path: Path to compiled binary
        compiler: Compiler type
        target_platform: Target platform
        num_iterations: Number of benchmark iterations

    Returns:
        Benchmark results
    """
    try:
        from app.utils.performance import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Create dummy input based on model
        # This is simplified - in production, use actual model metadata
        dummy_input = np.random.randn(1, 512).astype(np.float32)

        # Define inference function
        if compiler == CompilerType.TVM:
            tvm_compiler = TVMCompiler()

            def inference_func(input_data):
                return tvm_compiler.run_inference(
                    binary_path, target_platform, input_data
                )

        elif compiler == CompilerType.OPENXLA:
            xla_compiler = XLACompiler()
            dummy_input_tensor = torch.tensor(dummy_input)

            def inference_func(input_data):
                return xla_compiler.run_inference(binary_path, input_data)

            dummy_input = dummy_input_tensor
        else:
            raise ValueError(f"Unsupported compiler: {compiler}")

        # Run benchmark
        results = monitor.benchmark_inference(
            inference_func=inference_func,
            input_data=dummy_input,
            num_iterations=num_iterations,
        )

        results["binary_path"] = binary_path
        results["compiler"] = compiler.value
        results["target_platform"] = target_platform.value

        return results

    except Exception as e:
        logger.error(f"Benchmark error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
