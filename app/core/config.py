"""
Configuration management for the application.

This module provides configuration settings using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = "development"

    # Paths
    models_dir: str = "data/models"
    binaries_dir: str = "data/binaries"

    # TVM Settings
    tvm_target_x86: str = "llvm -mcpu=core-avx2"
    tvm_target_arm: str = "llvm -mtriple=aarch64-linux-gnu -mcpu=cortex-a72"

    # Compilation Settings
    optimization_level: int = 3
    use_auto_scheduler: bool = True
    quantization_enabled: bool = True

    # Model Settings
    max_sequence_length: int = 512
    batch_size: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
