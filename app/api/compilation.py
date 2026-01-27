"""
Compilation API endpoints.

This module provides REST API endpoints for compiling ML models
using TVM and OpenXLA compilers.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
import logging

from app.models.schemas import (
    CompilationRequest,
    CompilationResponse,
    CompilerType,
    TargetPlatform,
)
from app.services.tvm_compiler import TVMCompiler
from app.services.xla_compiler import XLACompiler
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store compilation jobs (in production, use a proper job queue)
compilation_jobs: Dict[str, Dict[str, Any]] = {}


@router.post("/compile", response_model=CompilationResponse)
async def compile_model(
    request: CompilationRequest, background_tasks: BackgroundTasks
):
    """
    Compile a model using the specified compiler and target platform.

    Args:
        request: Compilation request parameters
        background_tasks: FastAPI background tasks

    Returns:
        Compilation response with job ID
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Initialize job status
        compilation_jobs[job_id] = {
            "status": "pending",
            "model_name": request.model_name,
            "compiler": request.compiler,
            "target_platform": request.target_platform,
            "progress": 0,
        }

        # Add compilation to background tasks
        background_tasks.add_task(
            run_compilation,
            job_id=job_id,
            request=request,
        )

        logger.info(
            f"Started compilation job {job_id} for {request.model_name} "
            f"using {request.compiler.value} targeting {request.target_platform.value}"
        )

        return CompilationResponse(
            job_id=job_id,
            status="pending",
            model_name=request.model_name,
            compiler=request.compiler,
            target_platform=request.target_platform,
            message=f"Compilation job started with ID: {job_id}",
        )

    except Exception as e:
        logger.error(f"Error starting compilation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_compilation(job_id: str, request: CompilationRequest):
    """
    Background task to run model compilation.

    Args:
        job_id: Unique job identifier
        request: Compilation request parameters
    """
    try:
        compilation_jobs[job_id]["status"] = "running"
        compilation_jobs[job_id]["progress"] = 10

        # Construct model path
        from pathlib import Path

        model_path = Path(settings.models_dir) / f"{request.model_name}.onnx"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        compilation_jobs[job_id]["progress"] = 30

        # Compile based on compiler type
        if request.compiler == CompilerType.TVM:
            compiler = TVMCompiler()
            result = compiler.compile_model(
                model_path=str(model_path),
                model_name=request.model_name,
                target_platform=request.target_platform,
                use_quantization=request.use_quantization,
                use_auto_scheduler=request.use_auto_scheduler,
            )
        elif request.compiler == CompilerType.OPENXLA:
            # For XLA, we need TorchScript format
            model_path = Path(settings.models_dir) / f"{request.model_name}.pt"
            if not model_path.exists():
                raise FileNotFoundError(
                    f"TorchScript model not found: {model_path}"
                )

            compiler = XLACompiler()
            result = compiler.compile_model(
                model_path=str(model_path),
                model_name=request.model_name,
                target_platform=request.target_platform,
                use_quantization=request.use_quantization,
            )
        else:
            raise ValueError(f"Unsupported compiler: {request.compiler}")

        compilation_jobs[job_id]["progress"] = 100
        compilation_jobs[job_id]["status"] = "completed"
        compilation_jobs[job_id]["result"] = result
        compilation_jobs[job_id]["binary_path"] = result["binary_path"]

        logger.info(f"Compilation job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Compilation job {job_id} failed: {str(e)}")
        compilation_jobs[job_id]["status"] = "failed"
        compilation_jobs[job_id]["error"] = str(e)


@router.get("/compile/{job_id}")
async def get_compilation_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a compilation job.

    Args:
        job_id: Unique job identifier

    Returns:
        Job status and results
    """
    if job_id not in compilation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return compilation_jobs[job_id]


@router.get("/compile")
async def list_compilation_jobs() -> Dict[str, Any]:
    """
    List all compilation jobs.

    Returns:
        Dict of all compilation jobs
    """
    return {"jobs": compilation_jobs}


@router.delete("/compile/{job_id}")
async def delete_compilation_job(job_id: str) -> Dict[str, str]:
    """
    Delete a compilation job from the queue.

    Args:
        job_id: Unique job identifier

    Returns:
        Deletion confirmation
    """
    if job_id not in compilation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del compilation_jobs[job_id]
    return {"status": "deleted", "job_id": job_id}
