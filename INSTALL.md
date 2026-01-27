# Installation Guide

## Quick Start (Base Features Only)

The base installation includes FastAPI, PyTorch, ONNX, and all core features except TVM and XLA compilation.

```bash
# Run setup script
bash scripts/setup.sh

# Build and start
make build
make up
```

This will give you:
- ✅ Model export (PyTorch → ONNX/TorchScript)
- ✅ REST API
- ✅ Performance monitoring
- ⚠️ TVM compilation (requires manual installation)
- ⚠️ XLA compilation (uses PyTorch JIT as fallback)

## Full Installation with TVM

### Option 1: Using tlcpack (Easiest)

TVM can be installed from the tlcpack wheel repository:

```bash
# Install TVM
pip install tlcpack-nightly -f https://tlcpack.ai/wheels

# Verify installation
python -c "import tvm; print(tvm.__version__)"
```

Then rebuild your Docker container:
```bash
make build
make up
```

### Option 2: Using Conda

```bash
# Create conda environment
conda create -n model-compilation python=3.13
conda activate model-compilation

# Install TVM
conda install -c conda-forge tvm

# Install other requirements
pip install -r requirements-base.txt
```

### Option 3: Build from Source

For the latest features or custom builds:

```bash
# Clone TVM
git clone --recursive https://github.com/apache/tvm.git
cd tvm

# Build
mkdir build
cd build
cmake ..
make -j4

# Install Python package
cd ../python
pip install -e .
```

See full instructions: https://tvm.apache.org/docs/install/from_source.html

## Full Installation with PyTorch XLA

⚠️ **Important**: PyTorch XLA is **platform-specific** and **not available for most systems**.

### Platform Support

- ✅ **Linux x86_64 + Google Cloud TPU**: Full support
- ❌ **macOS**: Not supported (no pre-built wheels)
- ❌ **Windows**: Not supported
- ❌ **Apple Silicon (M1/M2)**: Not supported

### For Supported Platforms (Linux + TPU)

```bash
# Only works on Google Cloud with TPUs
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
```

### For All Other Platforms

**XLA is optional and will automatically fall back to PyTorch JIT**. The system provides:
- Full model compilation using PyTorch JIT (TorchScript)
- Similar optimizations without XLA
- No functionality loss

**Recommendation**: Use TVM instead for better cross-platform support (works on macOS, Linux, Windows).

## Docker Installation

### Development Mode

```bash
# Build container with base requirements
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f model-compilation
```

### Production Mode

```bash
# Build production container
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### Custom Dockerfile with TVM

If you want TVM in your Docker image, modify the Dockerfile:

```dockerfile
# After base requirements, add:
RUN pip install --no-cache-dir tlcpack-nightly -f https://tlcpack.ai/wheels
```

## Local Installation (Without Docker)

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake git llvm-14 llvm-14-dev libopenblas-dev
```

**macOS:**
```bash
brew install cmake llvm@14 openblas
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install base requirements
pip install -r requirements-base.txt

# Optional: Install TVM
pip install tlcpack-nightly -f https://tlcpack.ai/wheels

# Optional: Install XLA
pip install torch_xla -f https://storage.googleapis.com/libtpu-releases/index.html
```

### 3. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Create data directories
mkdir -p data/models data/binaries
```

### 4. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verification

### Test Base Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# List models
curl http://localhost:8000/api/v1/models
```

### Test TVM Installation

```bash
# Export a model
curl -X POST http://localhost:8000/api/v1/models/export \
  -H "Content-Type: application/json" \
  -d '{"model_name": "test_model", "model_type": "llm", "export_format": "onnx"}'

# Try TVM compilation
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "test_model",
    "model_type": "llm",
    "compiler": "tvm",
    "target_platform": "x86",
    "export_format": "onnx"
  }'
```

If TVM is not installed, you'll get a clear error message with installation instructions.

### Test XLA Installation

```bash
# Export to TorchScript
curl -X POST http://localhost:8000/api/v1/models/export \
  -H "Content-Type: application/json" \
  -d '{"model_name": "test_model", "model_type": "llm", "export_format": "torchscript"}'

# Try XLA compilation
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "test_model",
    "model_type": "llm",
    "compiler": "openxla",
    "target_platform": "x86",
    "export_format": "torchscript"
  }'
```

If XLA is not installed, it will fall back to PyTorch JIT compilation.

## Troubleshooting

### TVM Import Error

**Error**: `ImportError: No module named 'tvm'`

**Solution**:
```bash
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```

### XLA Import Error

**Error**: `ImportError: No module named 'torch_xla'`

**Solution**: XLA is optional. The system will use PyTorch JIT as fallback. To install:
```bash
pip install torch_xla -f https://storage.googleapis.com/libtpu-releases/index.html
```

### LLVM Not Found

**Error**: `error: llvm-config not found`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install llvm-14 llvm-14-dev

# macOS
brew install llvm@14
export PATH="/opt/homebrew/opt/llvm@14/bin:$PATH"
```

### Docker Build Fails

**Error**: TVM installation fails during Docker build

**Solution**: The Dockerfile includes a fallback. TVM installation failure won't stop the build:
```dockerfile
RUN pip install --no-cache-dir tlcpack-nightly -f https://tlcpack.ai/wheels || \
    echo "Warning: TVM installation failed. TVM features will not be available."
```

You can install TVM manually in the running container:
```bash
docker-compose exec model-compilation pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```

## Requirements

### Minimum Requirements (Base Features)
- Python 3.13
- 4GB RAM
- 2GB disk space

### Recommended Requirements (Full Features)
- Python 3.13
- 8GB RAM
- 10GB disk space
- LLVM 14
- Docker & Docker Compose

### Optional Requirements
- TVM (via tlcpack or conda)
- PyTorch XLA (for XLA compilation)
- GPU (for XLA/TPU acceleration)

## Platform-Specific Notes

### macOS
- Use Homebrew for system dependencies
- M1/M2 Macs: Some wheels may not be available, build from source

### Linux
- Ubuntu 20.04+ recommended
- LLVM 14 required for TVM

### Windows
- WSL2 recommended for Docker
- Native Windows support via virtual environment
- Visual Studio Build Tools required for compilation

## Next Steps

After installation:
1. Read [USAGE.md](USAGE.md) for usage examples
2. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for feature status
3. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
4. Visit http://localhost:8000/docs for API documentation

## Support

For issues:
- Check logs: `make logs` or `docker-compose logs`
- Review error messages for installation hints
- TVM issues: https://github.com/apache/tvm/issues
- PyTorch XLA issues: https://github.com/pytorch/xla/issues
