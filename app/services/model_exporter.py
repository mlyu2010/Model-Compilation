"""
Model export service for converting PyTorch models to ONNX/TorchScript.

This module provides utilities to export PyTorch models to various formats
for cross-framework compatibility.
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import logging

from app.models.schemas import ExportFormat, ModelType
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelExporter:
    """Service for exporting PyTorch models to different formats."""

    def __init__(self):
        """Initialize the model exporter."""
        self.models_dir = Path(settings.models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def export_to_onnx(
        self,
        model: nn.Module,
        dummy_input: torch.Tensor,
        output_path: str,
        input_names: list = None,
        output_names: list = None,
        dynamic_axes: Dict = None,
    ) -> str:
        """
        Export PyTorch model to ONNX format.

        Args:
            model: PyTorch model to export
            dummy_input: Sample input tensor for tracing
            output_path: Path to save the ONNX model
            input_names: Names of input nodes
            output_names: Names of output nodes
            dynamic_axes: Dynamic axes configuration

        Returns:
            str: Path to the exported ONNX model
        """
        model.eval()

        if input_names is None:
            input_names = ["input"]
        if output_names is None:
            output_names = ["output"]

        logger.info(f"Exporting model to ONNX: {output_path}")

        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes,
        )

        logger.info(f"Successfully exported to ONNX: {output_path}")
        return output_path

    def export_to_torchscript(
        self,
        model: nn.Module,
        dummy_input: torch.Tensor,
        output_path: str,
        use_tracing: bool = True,
    ) -> str:
        """
        Export PyTorch model to TorchScript format.

        Args:
            model: PyTorch model to export
            dummy_input: Sample input tensor for tracing
            output_path: Path to save the TorchScript model
            use_tracing: Whether to use tracing (vs scripting)

        Returns:
            str: Path to the exported TorchScript model
        """
        model.eval()

        logger.info(f"Exporting model to TorchScript: {output_path}")

        if use_tracing:
            traced_model = torch.jit.trace(model, dummy_input)
        else:
            traced_model = torch.jit.script(model)

        traced_model.save(output_path)

        logger.info(f"Successfully exported to TorchScript: {output_path}")
        return output_path

    def create_dummy_input(
        self, model_type: ModelType, batch_size: int = 1
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Create dummy input tensor based on model type.

        Args:
            model_type: Type of the model
            batch_size: Batch size for the input

        Returns:
            Tuple of dummy input tensor and metadata
        """
        if model_type == ModelType.LLM:
            # For LLM: (batch_size, sequence_length)
            seq_length = settings.max_sequence_length
            dummy_input = torch.randint(
                0, 1000, (batch_size, seq_length), dtype=torch.long
            )
            metadata = {
                "input_shape": (batch_size, seq_length),
                "input_names": ["input_ids"],
                "output_names": ["logits"],
                "dynamic_axes": {
                    "input_ids": {0: "batch_size", 1: "sequence"},
                    "logits": {0: "batch_size", 1: "sequence"},
                },
            }
        elif model_type == ModelType.KEYWORD_SPOTTING:
            # For KWS: (batch_size, channels, time_steps)
            # Assuming MFCC features: 40 mel channels, variable time steps
            channels = 40
            time_steps = 101
            dummy_input = torch.randn(batch_size, channels, time_steps)
            metadata = {
                "input_shape": (batch_size, channels, time_steps),
                "input_names": ["audio_features"],
                "output_names": ["predictions"],
                "dynamic_axes": {
                    "audio_features": {0: "batch_size", 2: "time"},
                    "predictions": {0: "batch_size"},
                },
            }
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        return dummy_input, metadata

    def export_model(
        self,
        model: nn.Module,
        model_name: str,
        model_type: ModelType,
        export_format: ExportFormat,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Export a PyTorch model to the specified format.

        Args:
            model: PyTorch model to export
            model_name: Name of the model
            model_type: Type of the model
            export_format: Target export format
            output_path: Optional custom output path

        Returns:
            Dict containing export results
        """
        # Create dummy input
        dummy_input, metadata = self.create_dummy_input(model_type)

        # Determine output path
        if output_path is None:
            extension = "onnx" if export_format == ExportFormat.ONNX else "pt"
            output_path = str(self.models_dir / f"{model_name}.{extension}")

        # Export based on format
        if export_format == ExportFormat.ONNX:
            exported_path = self.export_to_onnx(
                model=model,
                dummy_input=dummy_input,
                output_path=output_path,
                input_names=metadata["input_names"],
                output_names=metadata["output_names"],
                dynamic_axes=metadata["dynamic_axes"],
            )
        elif export_format == ExportFormat.TORCHSCRIPT:
            exported_path = self.export_to_torchscript(
                model=model,
                dummy_input=dummy_input,
                output_path=output_path,
            )
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        return {
            "model_name": model_name,
            "export_format": export_format.value,
            "output_path": exported_path,
            "metadata": metadata,
            "status": "success",
        }
