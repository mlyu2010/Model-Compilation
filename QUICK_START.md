# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.13
- Docker & Docker Compose (recommended)
- OR: pip and virtualenv

## Option 1: Docker (Recommended - Works Everywhere)

```bash
# 1. Setup
bash scripts/setup.sh

# 2. Build and start
make build
make up

# 3. Open your browser
open http://localhost:8000/docs
```

That's it! The API is now running with all base features.

## Option 2: Local Python Environment

```bash
# 1. Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-base.txt

# 3. Setup environment
cp .env.example .env
mkdir -p data/models data/binaries

# 4. Run the server
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs in your browser.

## What You Get Out of the Box

✅ **REST API** - FastAPI with interactive docs
✅ **Model Export** - PyTorch → ONNX/TorchScript
✅ **Model Management** - Upload, list, delete models
✅ **Performance Monitoring** - Latency, memory, throughput
✅ **PyTorch JIT Compilation** - TorchScript optimization

## Optional: Add TVM Support

TVM enables advanced compilation and optimization:

```bash
# Install TVM
pip install tlcpack-nightly -f https://tlcpack.ai/wheels

# Rebuild Docker if using containers
make build && make up
```

Now you can use TVM compilation features!

## Optional: Add XLA Support

⚠️ **Only for Linux x86_64 with Google Cloud TPU**

```bash
# Only works on supported platforms
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
```

If XLA is not available, the system automatically uses PyTorch JIT instead.

## First API Request

### 1. Export a Model

```bash
curl -X POST http://localhost:8000/api/v1/models/export \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_first_model",
    "model_type": "llm",
    "export_format": "onnx"
  }'
```

### 2. Check Available Models

```bash
curl http://localhost:8000/api/v1/models
```

### 3. Compile with TVM (if installed)

```bash
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "my_first_model",
    "model_type": "llm",
    "compiler": "tvm",
    "target_platform": "x86",
    "export_format": "onnx"
  }'
```

### 4. Check Compilation Status

```bash
# Use the job_id from step 3
curl http://localhost:8000/api/v1/compile/{job_id}
```

## Interactive API Documentation

Open http://localhost:8000/docs for:
- 📖 Full API documentation
- 🧪 Try out endpoints directly
- 📝 Request/response schemas
- 🔍 Search functionality

## Common Commands

```bash
# View logs
make logs

# Run tests
make test

# Generate docs
make docs

# Run benchmarks
make benchmark

# Stop everything
make down

# Clean up
make clean
```

## What's Next?

- 📖 Read [USAGE.md](USAGE.md) for detailed usage examples
- 🔧 Check [INSTALL.md](INSTALL.md) for advanced installation
- 🖥️ See [PLATFORM_SUPPORT.md](PLATFORM_SUPPORT.md) for platform-specific info
- 📊 Review [PROJECT_STATUS.md](PROJECT_STATUS.md) for feature status

## Troubleshooting

### "Port 8000 already in use"

```bash
# Stop any existing containers
docker-compose down

# Or change port in docker-compose.yml
```

### "Cannot connect to Docker daemon"

```bash
# Make sure Docker is running
docker ps

# On Linux, add user to docker group
sudo usermod -aG docker $USER
```

### "TVM not found"

This is expected if you haven't installed TVM yet. Install it:
```bash
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```

Or continue without TVM - all base features work without it.

### "XLA not available"

This is expected on macOS and Windows. XLA only works on Linux with TPU.
The system automatically uses PyTorch JIT instead - no functionality is lost.

## Need Help?

1. Check the error message - it usually tells you what to do
2. Review the documentation in the repository
3. Check logs: `make logs` or `docker-compose logs`
4. Visit http://localhost:8000/docs for API documentation

## Platform-Specific Quick Start

### macOS
```bash
# Base features work out of the box
pip install -r requirements-base.txt
uvicorn app.main:app --reload
```

### Linux
```bash
# Best platform - everything works
pip install -r requirements-base.txt
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
uvicorn app.main:app --reload
```

### Windows
```bash
# Use WSL2 + Docker for best experience
docker-compose build && docker-compose up
```

### Google Cloud (with TPU)
```bash
pip install -r requirements-base.txt
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
uvicorn app.main:app --reload
```

## Summary

**Minimum to get started:**
```bash
make build && make up
```

**Full features (with TVM):**
```bash
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
make build && make up
```

**That's it!** You now have a working ML model compilation API. 🎉
