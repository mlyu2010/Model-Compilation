"""
Pydantic models for API request/response schemas.

This module defines data models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class CompilerType(str, Enum):
    """Supported compiler types."""

    TVM = "tvm"
    OPENXLA = "openxla"


class TargetPlatform(str, Enum):
    """Target deployment platforms."""

    X86 = "x86"
    ARM = "arm"
    RASPBERRY_PI = "raspberry_pi"


class ModelType(str, Enum):
    """Supported model types."""

    LLM = "llm"
    KEYWORD_SPOTTING = "keyword_spotting"


class ExportFormat(str, Enum):
    """Model export formats."""

    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"


class CompilationRequest(BaseModel):
    """Request model for compilation."""

    model_name: str = Field(..., description="Name of the model to compile")
    model_type: ModelType = Field(..., description="Type of the model")
    compiler: CompilerType = Field(..., description="Compiler to use")
    target_platform: TargetPlatform = Field(..., description="Target platform")
    export_format: ExportFormat = Field(
        default=ExportFormat.ONNX, description="Export format"
    )
    optimization_level: int = Field(default=3, ge=0, le=3)
    use_quantization: bool = Field(default=True)
    use_auto_scheduler: bool = Field(default=True)


class CompilationResponse(BaseModel):
    """Response model for compilation."""

    job_id: str
    status: str
    model_name: str
    compiler: CompilerType
    target_platform: TargetPlatform
    message: str
    binary_path: Optional[str] = None


class InferenceRequest(BaseModel):
    """Request model for inference."""

    binary_path: str = Field(..., description="Path to compiled binary")
    input_data: Dict[str, Any] = Field(..., description="Input data for inference")
    batch_size: int = Field(default=1, ge=1)


class InferenceResponse(BaseModel):
    """Response model for inference."""

    predictions: List[Any]
    latency_ms: float
    memory_usage_mb: float
    throughput: float


class PerformanceMetrics(BaseModel):
    """Performance metrics model."""

    model_name: str
    compiler: CompilerType
    target_platform: TargetPlatform
    inference_latency_ms: float
    memory_usage_mb: float
    throughput: float
    compilation_time_s: float


class ModelExportRequest(BaseModel):
    """Request model for exporting PyTorch models."""

    model_name: str = Field(..., description="Name of the PyTorch model")
    model_type: ModelType = Field(..., description="Type of the model")
    export_format: ExportFormat = Field(..., description="Export format")
    output_path: Optional[str] = None


class ModelExportResponse(BaseModel):
    """Response model for model export."""

    model_name: str
    export_format: ExportFormat
    output_path: str
    status: str
    message: str
