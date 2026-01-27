# Model Compilation API - Usage Guide

## Quick Start

### 1. Start the Application

```bash
# Build and start containers
make build
make up

# Or using docker-compose directly
docker-compose build --no-cache
docker-compose up -d
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc

### 2. View Logs

```bash
make logs
# Or: docker-compose logs -f model-compilation
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Model Export

Export a PyTorch model to ONNX or TorchScript:

```bash
# Export LLM to ONNX
curl -X POST http://localhost:8000/api/v1/models/export \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_llm",
    "model_type": "llm",
    "export_format": "onnx"
  }'

# Export Keyword Spotting model to TorchScript
curl -X POST http://localhost:8000/api/v1/models/export \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_kws",
    "model_type": "keyword_spotting",
    "export_format": "torchscript"
  }'
```

### List Models

```bash
curl http://localhost:8000/api/v1/models
```

### Model Compilation

Compile a model using TVM or OpenXLA:

```bash
# Compile with TVM for x86
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_llm",
    "model_type": "llm",
    "compiler": "tvm",
    "target_platform": "x86",
    "export_format": "onnx",
    "optimization_level": 3,
    "use_quantization": true,
    "use_auto_scheduler": true
  }'

# Compile with OpenXLA for ARM
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_kws",
    "model_type": "keyword_spotting",
    "compiler": "openxla",
    "target_platform": "arm",
    "export_format": "torchscript",
    "use_quantization": true
  }'
```

### Check Compilation Status

```bash
# Replace <job_id> with the ID returned from the compile endpoint
curl http://localhost:8000/api/v1/compile/<job_id>
```

### Run Inference

```bash
# TVM inference
curl -X POST http://localhost:8000/api/v1/inference/tvm \
  -H "Content-Type: application/json" \
  -d '{
    "binary_path": "data/binaries/my_llm_x86_tvm.so",
    "input_data": {
      "input": [[1, 2, 3, 4, 5]]
    },
    "batch_size": 1
  }'

# XLA inference
curl -X POST http://localhost:8000/api/v1/inference/xla \
  -H "Content-Type: application/json" \
  -d '{
    "binary_path": "data/binaries/my_kws_arm_xla.pt",
    "input_data": {
      "input": [[1.0, 2.0, 3.0]]
    },
    "batch_size": 1
  }'
```

### Benchmark Inference

```bash
curl -X POST "http://localhost:8000/api/v1/inference/benchmark?binary_path=data/binaries/model.so&compiler=tvm&target_platform=x86&num_iterations=100"
```

## Using the Interactive API Documentation

Navigate to http://localhost:8000/docs for the Swagger UI interface where you can:
1. View all available endpoints
2. Test endpoints directly from the browser
3. See request/response schemas
4. Download OpenAPI specification

## Running Tests

```bash
# Run all tests
make test

# Or with docker-compose
docker-compose exec model-compilation pytest

# Run with coverage
docker-compose exec model-compilation pytest --cov=app --cov-report=html
```

## Generate Documentation

```bash
# Generate HTML documentation from docstrings
make docs

# Or with docker-compose
docker-compose exec model-compilation python scripts/generate_docs.py
```

## Running Benchmarks

```bash
# Run default benchmark
make benchmark

# Run custom benchmark
docker-compose exec model-compilation python scripts/run_benchmark.py \
  --model-name test_model \
  --model-type llm \
  --compilers tvm openxla \
  --platforms x86 arm
```

## Development Workflow

### 1. Export a Model

First, export your PyTorch model to ONNX (for TVM) or TorchScript (for XLA):

```python
# Example using the API
import requests

response = requests.post(
    "http://localhost:8000/api/v1/models/export",
    json={
        "model_name": "my_model",
        "model_type": "llm",
        "export_format": "onnx"
    }
)
print(response.json())
```

### 2. Compile the Model

Compile the exported model for your target platform:

```python
response = requests.post(
    "http://localhost:8000/api/v1/compile",
    json={
        "model_name": "my_model",
        "model_type": "llm",
        "compiler": "tvm",
        "target_platform": "x86",
        "export_format": "onnx"
    }
)
job = response.json()
job_id = job["job_id"]
```

### 3. Check Compilation Status

```python
import time

while True:
    response = requests.get(f"http://localhost:8000/api/v1/compile/{job_id}")
    status = response.json()

    if status["status"] == "completed":
        print(f"Compilation completed! Binary: {status['binary_path']}")
        break
    elif status["status"] == "failed":
        print(f"Compilation failed: {status.get('error')}")
        break

    print(f"Status: {status['status']}, Progress: {status.get('progress', 0)}%")
    time.sleep(2)
```

### 4. Run Inference

```python
response = requests.post(
    "http://localhost:8000/api/v1/inference/tvm",
    json={
        "binary_path": status["binary_path"],
        "input_data": {"input": [[1, 2, 3, 4, 5]]},
        "batch_size": 1
    }
)
results = response.json()
print(f"Latency: {results['latency_ms']}ms")
print(f"Throughput: {results['throughput']} QPS")
```

## Production Deployment

For production deployment, use the production docker-compose file:

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Cleanup

```bash
# Stop services and clean up
make clean

# Or manually
docker-compose down -v
rm -rf data/models/* data/binaries/*
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs model-compilation
```

### Out of memory during compilation

Reduce optimization level or disable auto-scheduler in the compilation request.

### Model not found

Ensure you've exported the model first and check the models directory:
```bash
docker-compose exec model-compilation ls -la data/models/
```

## Configuration

Environment variables can be set in `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your settings
```

Key configuration options:
- `OPTIMIZATION_LEVEL`: TVM optimization level (0-3)
- `USE_AUTO_SCHEDULER`: Enable TVM auto-scheduler
- `QUANTIZATION_ENABLED`: Enable model quantization
- `MAX_SEQUENCE_LENGTH`: Maximum sequence length for LLM models
