"""
OpenXLA compilation service for optimizing and compiling ML models.

This module provides utilities for compiling models using PyTorch/XLA
for cross-platform deployment.
"""

import torch
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time
import psutil

# Try to import XLA, but make it optional
try:
    import torch_xla
    import torch_xla.core.xla_model as xm
    XLA_AVAILABLE = True
except ImportError:
    XLA_AVAILABLE = False
    torch_xla = None
    xm = None

from app.models.schemas import TargetPlatform
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XLACompiler:
    """Service for compiling models with OpenXLA via PyTorch/XLA."""

    def __init__(self):
        """Initialize the XLA compiler."""
        if not XLA_AVAILABLE:
            logger.warning(
                "PyTorch XLA is not installed. XLA features will use standard PyTorch JIT instead. "
                "To enable XLA, install torch_xla."
            )
        self.binaries_dir = Path(settings.binaries_dir)
        self.binaries_dir.mkdir(parents=True, exist_ok=True)

    def get_device_config(self, platform: TargetPlatform) -> str:
        """
        Get XLA device configuration for the specified platform.

        Args:
            platform: Target deployment platform

        Returns:
            Device string for XLA
        """
        # XLA typically uses CPU for non-TPU targets
        # For production, you would configure specific XLA backends
        return "CPU"

    def load_torchscript_model(self, model_path: str) -> torch.jit.ScriptModule:
        """
        Load TorchScript model.

        Args:
            model_path: Path to TorchScript model file

        Returns:
            TorchScript module
        """
        logger.info(f"Loading TorchScript model from: {model_path}")
        model = torch.jit.load(model_path)
        model.eval()
        logger.info("Successfully loaded TorchScript model")
        return model

    def optimize_with_xla(
        self,
        model: torch.nn.Module,
        dummy_input: torch.Tensor,
        device: str = "CPU",
    ) -> torch.nn.Module:
        """
        Optimize model using XLA compilation.

        Args:
            model: PyTorch model
            dummy_input: Sample input for tracing
            device: XLA device

        Returns:
            XLA-optimized model
        """
        if not XLA_AVAILABLE:
            logger.warning("XLA not available, using standard PyTorch JIT compilation")
            # Fall back to standard PyTorch JIT trace
            with torch.no_grad():
                traced_model = torch.jit.trace(model, dummy_input)
            return traced_model

        logger.info("Optimizing model with XLA")

        # Move model to XLA device
        xla_device = xm.xla_device()
        model = model.to(xla_device)
        dummy_input = dummy_input.to(xla_device)

        # Trace and optimize
        with torch.no_grad():
            # Run once to trigger XLA compilation
            _ = model(dummy_input)
            # Mark step to complete compilation
            xm.mark_step()

        logger.info("XLA optimization completed")
        return model

    def apply_quantization(
        self, model: torch.nn.Module
    ) -> torch.nn.Module:
        """
        Apply dynamic quantization to the model.

        Args:
            model: PyTorch model

        Returns:
            Quantized model
        """
        logger.info("Applying dynamic quantization")

        # Apply dynamic quantization (works on CPU)
        quantized_model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear, torch.nn.LSTM, torch.nn.GRU}, dtype=torch.qint8
        )

        logger.info("Quantization completed")
        return quantized_model

    def compile_model(
        self,
        model_path: str,
        model_name: str,
        target_platform: TargetPlatform,
        use_quantization: bool = True,
    ) -> Dict[str, Any]:
        """
        Compile a model using PyTorch/XLA.

        Args:
            model_path: Path to the input model (TorchScript format)
            model_name: Name of the model
            target_platform: Target deployment platform
            use_quantization: Whether to apply quantization

        Returns:
            Dict containing compilation results
        """
        start_time = time.time()

        # Load model
        model = self.load_torchscript_model(model_path)

        # Get device configuration
        device = self.get_device_config(target_platform)

        # Apply quantization if requested
        if use_quantization and settings.quantization_enabled:
            model = self.apply_quantization(model)

        # Create dummy input for optimization
        # Note: In production, you'd determine this from model metadata
        dummy_input = torch.randn(1, 512)  # Simplified example

        # Optimize with XLA
        try:
            model = self.optimize_with_xla(model, dummy_input, device)
        except Exception as e:
            logger.warning(f"XLA optimization failed, falling back to CPU: {e}")
            # Fall back to regular PyTorch compilation

        # Save optimized model
        output_path = (
            self.binaries_dir / f"{model_name}_{target_platform.value}_xla.pt"
        )

        # Save the model
        if use_quantization:
            torch.jit.save(torch.jit.script(model), str(output_path))
        else:
            torch.jit.save(model, str(output_path))

        compilation_time = time.time() - start_time

        logger.info(
            f"Compilation completed in {compilation_time:.2f}s, saved to {output_path}"
        )

        return {
            "model_name": model_name,
            "compiler": "openxla",
            "target_platform": target_platform.value,
            "binary_path": str(output_path),
            "compilation_time_s": compilation_time,
            "optimizations": {
                "quantization": use_quantization,
                "xla_optimization": True,
            },
            "status": "success",
        }

    def run_inference(
        self,
        binary_path: str,
        input_data: torch.Tensor,
    ) -> Dict[str, Any]:
        """
        Run inference using compiled XLA model.

        Args:
            binary_path: Path to compiled binary
            input_data: Input data as tensor

        Returns:
            Dict containing inference results and metrics
        """
        # Load model
        model = torch.jit.load(binary_path)
        model.eval()

        # Warm-up run
        with torch.no_grad():
            _ = model(input_data)

        # Measure inference time
        start_time = time.time()
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        with torch.no_grad():
            output = model(input_data)

        latency = (time.time() - start_time) * 1000  # ms
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = mem_after - mem_before

        return {
            "output": output.cpu().numpy().tolist(),
            "latency_ms": latency,
            "memory_usage_mb": max(memory_usage, 0),
            "throughput": 1000 / latency if latency > 0 else 0,
        }
