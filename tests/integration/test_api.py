"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_models(client):
    """Test listing models."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "onnx_models" in data
    assert "torchscript_models" in data
    assert "total_count" in data


def test_export_model_llm(client):
    """Test exporting LLM model."""
    request_data = {
        "model_name": "test_llm",
        "model_type": "llm",
        "export_format": "onnx",
    }
    response = client.post("/api/v1/models/export", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "test_llm"
    assert data["export_format"] == "onnx"
    assert data["status"] == "success"


def test_export_model_kws(client):
    """Test exporting KWS model."""
    request_data = {
        "model_name": "test_kws",
        "model_type": "keyword_spotting",
        "export_format": "torchscript",
    }
    response = client.post("/api/v1/models/export", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "test_kws"
    assert data["export_format"] == "torchscript"
    assert data["status"] == "success"


def test_compile_endpoint(client):
    """Test compilation endpoint."""
    request_data = {
        "model_name": "test_model",
        "model_type": "llm",
        "compiler": "tvm",
        "target_platform": "x86",
        "export_format": "onnx",
    }
    response = client.post("/api/v1/compile", json=request_data)
    # Expect 200 for job creation (even if compilation fails in background)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_list_compilation_jobs(client):
    """Test listing compilation jobs."""
    response = client.get("/api/v1/compile")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
