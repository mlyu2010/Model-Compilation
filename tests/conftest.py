"""
Pytest configuration and shared fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def temp_models_dir():
    """Create temporary models directory."""
    temp_dir = tempfile.mkdtemp()
    original_dir = settings.models_dir
    settings.models_dir = temp_dir
    yield temp_dir
    settings.models_dir = original_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_binaries_dir():
    """Create temporary binaries directory."""
    temp_dir = tempfile.mkdtemp()
    original_dir = settings.binaries_dir
    settings.binaries_dir = temp_dir
    yield temp_dir
    settings.binaries_dir = original_dir
    shutil.rmtree(temp_dir, ignore_errors=True)
