"""
Unit tests for model exporter service.
"""

import pytest
import torch
import torch.nn as nn
from pathlib import Path

from app.services.model_exporter import ModelExporter
from app.models.schemas import ModelType, ExportFormat


class SimpleModel(nn.Module):
    """Simple model for testing."""

    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 5)

    def forward(self, x):
        return self.fc(x)


def test_create_dummy_input_llm():
    """Test creating dummy input for LLM model."""
    exporter = ModelExporter()
    dummy_input, metadata = exporter.create_dummy_input(ModelType.LLM)

    assert dummy_input.shape[1] == 512  # sequence length
    assert "input_names" in metadata
    assert "output_names" in metadata


def test_create_dummy_input_kws():
    """Test creating dummy input for KWS model."""
    exporter = ModelExporter()
    dummy_input, metadata = exporter.create_dummy_input(ModelType.KEYWORD_SPOTTING)

    assert dummy_input.shape[1] == 40  # mel channels
    assert "input_names" in metadata
    assert "output_names" in metadata


def test_export_to_onnx(temp_models_dir):
    """Test ONNX export."""
    exporter = ModelExporter()
    model = SimpleModel()
    dummy_input = torch.randn(1, 10)
    output_path = str(Path(temp_models_dir) / "test_model.onnx")

    result_path = exporter.export_to_onnx(
        model=model,
        dummy_input=dummy_input,
        output_path=output_path,
    )

    assert Path(result_path).exists()
    assert result_path.endswith(".onnx")


def test_export_to_torchscript(temp_models_dir):
    """Test TorchScript export."""
    exporter = ModelExporter()
    model = SimpleModel()
    dummy_input = torch.randn(1, 10)
    output_path = str(Path(temp_models_dir) / "test_model.pt")

    result_path = exporter.export_to_torchscript(
        model=model,
        dummy_input=dummy_input,
        output_path=output_path,
    )

    assert Path(result_path).exists()
    assert result_path.endswith(".pt")
