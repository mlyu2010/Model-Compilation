"""
Model management API endpoints.

This module provides REST API endpoints for managing and exporting models.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any
import logging
from pathlib import Path

from app.models.schemas import (
    ModelExportRequest,
    ModelExportResponse,
    ModelType,
    ExportFormat,
)
from app.services.model_exporter import ModelExporter
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/models/export", response_model=ModelExportResponse)
async def export_model(request: ModelExportRequest):
    """
    Export a PyTorch model to ONNX or TorchScript format.

    Note: This endpoint expects the PyTorch model to be already available
    or provides a placeholder implementation. In production, you would
    load the actual model from Hugging Face or a model registry.

    Args:
        request: Model export request

    Returns:
        Export results
    """
    try:
        exporter = ModelExporter()

        # Create a placeholder model for demonstration
        # In production, load the actual model
        import torch.nn as nn

        if request.model_type == ModelType.LLM:
            # Placeholder LLM model
            class SimpleLLM(nn.Module):
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

            model = SimpleLLM()

        elif request.model_type == ModelType.KEYWORD_SPOTTING:
            # Placeholder KWS model
            class SimpleKWS(nn.Module):
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

            import torch

            model = SimpleKWS()
        else:
            raise ValueError(f"Unsupported model type: {request.model_type}")

        # Export the model
        result = exporter.export_model(
            model=model,
            model_name=request.model_name,
            model_type=request.model_type,
            export_format=request.export_format,
            output_path=request.output_path,
        )

        return ModelExportResponse(
            model_name=result["model_name"],
            export_format=request.export_format,
            output_path=result["output_path"],
            status=result["status"],
            message=f"Model exported successfully to {result['export_format']} format",
        )

    except Exception as e:
        logger.error(f"Model export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """
    List all available models in the models directory.

    Returns:
        List of model files grouped by format
    """
    try:
        models_dir = Path(settings.models_dir)
        models_dir.mkdir(parents=True, exist_ok=True)

        onnx_models = [f.name for f in models_dir.glob("*.onnx")]
        torchscript_models = [f.name for f in models_dir.glob("*.pt")]

        return {
            "onnx_models": onnx_models,
            "torchscript_models": torchscript_models,
            "total_count": len(onnx_models) + len(torchscript_models),
        }

    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}")
async def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific model.

    Args:
        model_name: Name of the model (without extension)

    Returns:
        Model information
    """
    try:
        models_dir = Path(settings.models_dir)

        # Check for model files
        onnx_path = models_dir / f"{model_name}.onnx"
        torchscript_path = models_dir / f"{model_name}.pt"

        info = {"model_name": model_name, "formats": []}

        if onnx_path.exists():
            info["formats"].append(
                {
                    "format": "onnx",
                    "path": str(onnx_path),
                    "size_mb": onnx_path.stat().st_size / 1024 / 1024,
                }
            )

        if torchscript_path.exists():
            info["formats"].append(
                {
                    "format": "torchscript",
                    "path": str(torchscript_path),
                    "size_mb": torchscript_path.stat().st_size / 1024 / 1024,
                }
            )

        if not info["formats"]:
            raise HTTPException(status_code=404, detail="Model not found")

        return info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_name}")
async def delete_model(model_name: str, format: str = None) -> Dict[str, str]:
    """
    Delete a model file.

    Args:
        model_name: Name of the model (without extension)
        format: Optional format to delete (onnx or torchscript)

    Returns:
        Deletion confirmation
    """
    try:
        models_dir = Path(settings.models_dir)
        deleted = []

        if format == "onnx" or format is None:
            onnx_path = models_dir / f"{model_name}.onnx"
            if onnx_path.exists():
                onnx_path.unlink()
                deleted.append("onnx")

        if format == "torchscript" or format is None:
            torchscript_path = models_dir / f"{model_name}.pt"
            if torchscript_path.exists():
                torchscript_path.unlink()
                deleted.append("torchscript")

        if not deleted:
            raise HTTPException(status_code=404, detail="Model not found")

        return {
            "status": "deleted",
            "model_name": model_name,
            "formats_deleted": deleted,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
