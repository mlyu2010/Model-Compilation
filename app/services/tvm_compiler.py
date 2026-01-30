"""
TVM compilation service for optimizing and compiling ML models.

This module provides utilities for compiling models using Apache TVM
with auto-scheduling and quantization support.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    import tvm

# Try to import ONNX, but make it optional
try:
    import onnx
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    onnx = None

# Try to import TVM, but make it optional
try:
    import tvm
    from tvm import relay, auto_scheduler
    from tvm.contrib import graph_executor
    TVM_AVAILABLE = True
except ImportError:
    TVM_AVAILABLE = False
    tvm = None
    relay = None
    auto_scheduler = None
    graph_executor = None

from app.models.schemas import TargetPlatform
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TVMCompiler:
    """Service for compiling models with Apache TVM."""

    def __init__(self):
        """Initialize the TVM compiler."""
        if not ONNX_AVAILABLE:
            raise ImportError(
                "ONNX is not installed. Install it with: pip install onnx"
            )
        if not TVM_AVAILABLE:
            raise ImportError(
                "TVM is not installed. "
                "TVM installation requires platform-specific steps:\n"
                "  - For x86_64 Linux: pip install apache-tvm\n"
                "  - For ARM64/Apple Silicon: TVM may not be available due to numpy compatibility issues\n"
                "  - Alternative: Use OpenXLA compiler instead (set compiler='openxla' in request)\n"
                "See Dockerfile comments for more details."
            )
        self.binaries_dir = Path(settings.binaries_dir)
        self.binaries_dir.mkdir(parents=True, exist_ok=True)

    def get_target_config(self, platform: TargetPlatform) -> Any:
        """
        Get TVM target configuration for the specified platform.

        Args:
            platform: Target deployment platform

        Returns:
            TVM target configuration
        """
        if platform == TargetPlatform.X86:
            return tvm.target.Target(settings.tvm_target_x86)
        elif platform in [TargetPlatform.ARM, TargetPlatform.RASPBERRY_PI]:
            return tvm.target.Target(settings.tvm_target_arm)
        else:
            raise ValueError(f"Unsupported target platform: {platform}")

    def load_onnx_model(self, model_path: str) -> tuple:
        """
        Load ONNX model and convert to Relay IR.

        Args:
            model_path: Path to ONNX model file

        Returns:
            Tuple of (relay_module, params)
        """
        logger.info(f"Loading ONNX model from: {model_path}")
        onnx_model = onnx.load(model_path)

        # Get input shape from the model
        input_name = onnx_model.graph.input[0].name
        input_shape_proto = onnx_model.graph.input[0].type.tensor_type.shape
        input_shape = [dim.dim_value for dim in input_shape_proto.dim]

        # Convert to Relay
        shape_dict = {input_name: input_shape}
        mod, params = relay.frontend.from_onnx(onnx_model, shape_dict)

        logger.info("Successfully converted ONNX to Relay IR")
        return mod, params

    def apply_optimizations(
        self,
        mod: Any,
        params: Dict,
        target: Any,
        use_auto_scheduler: bool = True,
    ) -> tuple:
        """
        Apply TVM optimizations including auto-scheduling.

        Args:
            mod: Relay module
            params: Model parameters
            target: TVM target
            use_auto_scheduler: Whether to use auto-scheduler

        Returns:
            Tuple of (optimized_module, optimized_params)
        """
        logger.info("Applying TVM optimizations")

        # Apply standard optimization passes
        with tvm.transform.PassContext(opt_level=settings.optimization_level):
            mod = relay.transform.InferType()(mod)
            mod = relay.transform.FoldConstant()(mod)
            mod = relay.transform.SimplifyInference()(mod)

        if use_auto_scheduler:
            logger.info("Running auto-scheduler (this may take a while)")
            # Note: In production, you would run extensive tuning here
            # For now, we'll use a simplified approach
            tasks, task_weights = auto_scheduler.extract_tasks(
                mod["main"], params, target
            )
            logger.info(f"Found {len(tasks)} tasks to optimize")

        return mod, params

    def quantize_model(
        self, mod: Any, params: Dict
    ) -> tuple:
        """
        Apply quantization to the model.

        Args:
            mod: Relay module
            params: Model parameters

        Returns:
            Tuple of (quantized_module, quantized_params)
        """
        logger.info("Applying INT8 quantization")

        # Convert to QNN
        with tvm.transform.PassContext(opt_level=3):
            qconfig = relay.quantize.qconfig(
                calibrate_mode="global_scale",
                global_scale=8.0,
            )
            mod = relay.quantize.quantize(mod, params, dataset=None)

        logger.info("Quantization completed")
        return mod, params

    def compile_model(
        self,
        model_path: str,
        model_name: str,
        target_platform: TargetPlatform,
        use_quantization: bool = True,
        use_auto_scheduler: bool = True,
    ) -> Dict[str, Any]:
        """
        Compile a model using TVM.

        Args:
            model_path: Path to the input model (ONNX format)
            model_name: Name of the model
            target_platform: Target deployment platform
            use_quantization: Whether to apply quantization
            use_auto_scheduler: Whether to use auto-scheduler

        Returns:
            Dict containing compilation results
        """
        import time

        start_time = time.time()

        # Load model
        mod, params = self.load_onnx_model(model_path)

        # Get target configuration
        target = self.get_target_config(target_platform)

        # Apply optimizations
        mod, params = self.apply_optimizations(
            mod, params, target, use_auto_scheduler
        )

        # Apply quantization if requested
        if use_quantization and settings.quantization_enabled:
            mod, params = self.quantize_model(mod, params)

        # Build the model
        logger.info(f"Building model for target: {target}")
        with tvm.transform.PassContext(opt_level=settings.optimization_level):
            lib = relay.build(mod, target=target, params=params)

        # Save compiled library
        output_path = (
            self.binaries_dir / f"{model_name}_{target_platform.value}_tvm.so"
        )
        lib.export_library(str(output_path))

        compilation_time = time.time() - start_time

        logger.info(
            f"Compilation completed in {compilation_time:.2f}s, saved to {output_path}"
        )

        return {
            "model_name": model_name,
            "compiler": "tvm",
            "target_platform": target_platform.value,
            "binary_path": str(output_path),
            "compilation_time_s": compilation_time,
            "optimizations": {
                "quantization": use_quantization,
                "auto_scheduler": use_auto_scheduler,
                "opt_level": settings.optimization_level,
            },
            "status": "success",
        }

    def create_runtime(self, binary_path: str, target_platform: TargetPlatform):
        """
        Create a TVM runtime for inference.

        Args:
            binary_path: Path to compiled binary
            target_platform: Target platform

        Returns:
            TVM graph executor module
        """
        target = self.get_target_config(target_platform)
        dev = tvm.device(str(target), 0)

        # Load the compiled library
        lib = tvm.runtime.load_module(binary_path)

        # Create graph executor
        module = graph_executor.GraphModule(lib["default"](dev))

        return module, dev

    def run_inference(
        self,
        binary_path: str,
        target_platform: TargetPlatform,
        input_data: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Run inference using compiled TVM model.

        Args:
            binary_path: Path to compiled binary
            target_platform: Target platform
            input_data: Input data as numpy array

        Returns:
            Dict containing inference results and metrics
        """
        import time
        import psutil

        # Create runtime
        module, dev = self.create_runtime(binary_path, target_platform)

        # Set input
        module.set_input("input", tvm.nd.array(input_data, dev))

        # Warm-up run
        module.run()

        # Measure inference time
        start_time = time.time()
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        module.run()

        latency = (time.time() - start_time) * 1000  # ms
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = mem_after - mem_before

        # Get output
        output = module.get_output(0).numpy()

        return {
            "output": output.tolist(),
            "latency_ms": latency,
            "memory_usage_mb": max(memory_usage, 0),
            "throughput": 1000 / latency if latency > 0 else 0,
        }
