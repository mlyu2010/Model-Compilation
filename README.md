This project focuses on evaluating Apache TVM and OpenXLA as ML compilers for deploying two 
BrainChip's Akida TENNs models (a Large Language Model and a Keyword Spotting Model) across 
x86 and ARM processors. The project implements optimized workflows for both frameworks,
analyze performance metrics, and document best practices for deployment.

## Dependencies
1. Docker
2. Docker Compose
3. Python 3.13

## Description
- Set up development environments for TVM (using Hugging Face integration) and XLA (via PyTorch/XLA).
- Export both PyTorch models to ONNX or TorchScript for cross-framework compatibility.
- Implement TVM and OpenXLA compilation pipelines for both models.
- Optimize using auto-scheduling and quantization tools.
- Generate binaries for x86 and ARM targets (e.g., Raspberry Pi).
- Test on multiple devices and compare metrics: Inference Latency, Memory Usage, Cross-Platform Consistency
- Create reproducible scripts for both workflows.
- Draft a performance analysis report with recommendations.

## Features

- FastAPI Framework: Modern, fast Python web framework
- Docker Support: Full Docker and docker-compose setup
- Comprehensive Tests: Unit and integration tests included
- API Documentation and Testing via Web UI: http://localhost:8000/docs
- Production and Development Environments: 'docker-compose.yml' and 'docker-compose.prod.yml' files included

## Installation

docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f model-compilation

## Documentation

### Generating HTML Documentation

The project includes comprehensive docstrings throughout the codebase.
You can generate beautiful HTML documentation via
scripts/generate_docs.py