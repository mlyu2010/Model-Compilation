# Platform Support Guide

## Quick Reference

| Feature | macOS | Linux | Windows | Apple Silicon |
|---------|-------|-------|---------|---------------|
| **Base API** | ✅ | ✅ | ✅ | ✅ |
| **Model Export** | ✅ | ✅ | ✅ | ✅ |
| **PyTorch** | ✅ | ✅ | ✅ | ✅ |
| **ONNX** | ✅ | ✅ | ✅ | ✅ |
| **TVM** | ✅ | ✅ | ✅ | ⚠️ |
| **XLA** | ❌ | ⚠️ | ❌ | ❌ |

Legend:
- ✅ Fully supported
- ⚠️ Limited support / requires special setup
- ❌ Not supported

## Detailed Platform Support

### macOS (Intel)

**Supported Features:**
- ✅ FastAPI REST API
- ✅ Model export (PyTorch → ONNX/TorchScript)
- ✅ PyTorch inference
- ✅ TVM compilation (via tlcpack or conda)
- ✅ Docker containers

**Not Supported:**
- ❌ PyTorch XLA (no pre-built wheels)

**Installation:**
```bash
# Base features
pip install -r requirements-base.txt

# TVM (optional)
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
# OR
conda install -c conda-forge tvm

# XLA: Not available - will use PyTorch JIT fallback
```

### macOS (Apple Silicon M1/M2/M3)

**Supported Features:**
- ✅ FastAPI REST API
- ✅ Model export (PyTorch → ONNX/TorchScript)
- ✅ PyTorch inference (ARM optimized)
- ⚠️ TVM compilation (may need to build from source)
- ✅ Docker containers (via Rosetta or ARM builds)

**Not Supported:**
- ❌ PyTorch XLA

**Installation:**
```bash
# Base features
pip install -r requirements-base.txt

# TVM: May require building from source
git clone --recursive https://github.com/apache/tvm.git
cd tvm && mkdir build && cd build
cmake .. && make -j8
cd ../python && pip install -e .

# XLA: Not available - will use PyTorch JIT fallback
```

### Linux (x86_64)

**Supported Features:**
- ✅ FastAPI REST API
- ✅ Model export (PyTorch → ONNX/TorchScript)
- ✅ PyTorch inference
- ✅ TVM compilation
- ⚠️ XLA (only with Google Cloud TPU)

**Installation:**
```bash
# Base features
pip install -r requirements-base.txt

# TVM
pip install tlcpack-nightly -f https://tlcpack.ai/wheels

# XLA (only on Google Cloud with TPU)
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
```

**Recommended for:**
- Production deployments
- Full TVM support
- Docker deployments

### Linux (ARM/AArch64)

**Supported Features:**
- ✅ FastAPI REST API
- ✅ Model export
- ✅ PyTorch inference
- ⚠️ TVM compilation (build from source)

**Not Supported:**
- ❌ PyTorch XLA

**Use Cases:**
- Raspberry Pi deployment
- ARM edge devices
- Target platform for cross-compilation

### Windows

**Supported Features:**
- ✅ FastAPI REST API
- ✅ Model export
- ✅ PyTorch inference
- ⚠️ TVM compilation (requires Visual Studio Build Tools)
- ✅ Docker via WSL2

**Not Supported:**
- ❌ PyTorch XLA

**Installation:**
```bash
# Base features
pip install -r requirements-base.txt

# TVM: Requires Visual Studio Build Tools
# Recommended: Use WSL2 + Docker instead
```

**Recommendation:** Use WSL2 + Docker for best experience on Windows.

## Docker Support

### All Platforms

Docker provides consistent environments across all platforms:

```bash
# Works on macOS, Linux, Windows
docker-compose build
docker-compose up
```

**What Docker Includes:**
- ✅ Base Python environment
- ✅ All required system dependencies
- ✅ LLVM 14 for TVM compilation
- ⚠️ TVM (best-effort installation, may fail)
- ❌ XLA (not included)

**Advantages:**
- Consistent environment across platforms
- All system dependencies pre-installed
- Easy deployment and scaling

## Compiler Availability by Platform

### Apache TVM

| Platform | Installation Method | Status |
|----------|-------------------|--------|
| macOS Intel | tlcpack / conda | ✅ Easy |
| macOS ARM | Source build | ⚠️ Moderate |
| Linux x86_64 | tlcpack / conda | ✅ Easy |
| Linux ARM | Source build | ⚠️ Moderate |
| Windows | Source build / WSL2 | ⚠️ Moderate |

### PyTorch XLA

| Platform | Installation Method | Status |
|----------|-------------------|--------|
| macOS | N/A | ❌ Not available |
| Linux x86_64 | pip (TPU only) | ⚠️ TPU required |
| Linux ARM | N/A | ❌ Not available |
| Windows | N/A | ❌ Not available |

## Recommendations by Use Case

### Development (Any Platform)

**Recommended:**
```bash
# Install base requirements
pip install -r requirements-base.txt

# Try TVM if desired (optional)
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```

**Features Available:**
- Model export and management
- REST API
- PyTorch JIT compilation (XLA fallback)
- Performance benchmarking

### Production (Linux x86_64)

**Recommended:**
```bash
# Use Docker for consistency
docker-compose -f docker-compose.prod.yml up -d
```

**Or install natively:**
```bash
pip install -r requirements-base.txt
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```

**Features Available:**
- All base features
- Full TVM compilation
- Cross-platform binary generation
- Optimized performance

### Google Cloud TPU

**Recommended:**
```bash
pip install -r requirements-base.txt
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
```

**Features Available:**
- All base features
- Full XLA support with TPU acceleration
- Best performance for supported models

### Edge Devices (Raspberry Pi, ARM)

**Target Platform:**
Use TVM to compile binaries on x86_64, then deploy to ARM:

```bash
# On development machine (x86_64)
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{"compiler": "tvm", "target_platform": "arm"}'

# Deploy generated .so file to ARM device
scp data/binaries/model_arm_tvm.so pi@raspberrypi:/app/
```

## Troubleshooting by Platform

### macOS: "TVM not found"

**Solution:**
```bash
# Try tlcpack
pip install tlcpack-nightly -f https://tlcpack.ai/wheels

# If fails, try conda
conda install -c conda-forge tvm

# If both fail, build from source (takes ~30 min)
brew install llvm@14
git clone --recursive https://github.com/apache/tvm.git
cd tvm && mkdir build && cd build
cmake .. -DUSE_LLVM=$(brew --prefix llvm@14)/bin/llvm-config
make -j8
cd ../python && pip install -e .
```

### macOS: "XLA not available"

**This is expected.** XLA is not supported on macOS. The system will automatically use PyTorch JIT compilation instead, which provides similar optimization without XLA.

### Linux: "permission denied" in Docker

**Solution:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Windows: TVM installation fails

**Solution:**
Use WSL2 + Docker:
```bash
# In WSL2
docker-compose build
docker-compose up
```

## Testing Platform Support

### Check what's available:

```python
# Check TVM
try:
    import tvm
    print(f"✅ TVM available: {tvm.__version__}")
except ImportError:
    print("❌ TVM not available")

# Check XLA
try:
    import torch_xla
    print("✅ XLA available")
except ImportError:
    print("❌ XLA not available (will use PyTorch JIT)")
```

### Via API:

```bash
# Check API health
curl http://localhost:8000/health

# Try model export (works everywhere)
curl -X POST http://localhost:8000/api/v1/models/export \
  -H "Content-Type: application/json" \
  -d '{"model_name": "test", "model_type": "llm", "export_format": "onnx"}'

# Try TVM compilation (requires TVM)
curl -X POST http://localhost:8000/api/v1/compile \
  -H "Content-Type: application/json" \
  -d '{"model_name": "test", "compiler": "tvm", "target_platform": "x86"}'
```

## Summary

### What Works Everywhere
- ✅ FastAPI REST API
- ✅ Model export (ONNX/TorchScript)
- ✅ PyTorch inference
- ✅ Performance monitoring
- ✅ Docker containers

### What Needs Special Setup
- ⚠️ TVM: Needs manual installation, but available on most platforms
- ⚠️ XLA: Only on Linux + Google Cloud TPU

### Recommended Setup
- **Development**: Base requirements + TVM (optional)
- **Production**: Docker on Linux with TVM
- **Cloud**: Google Cloud with XLA + TPU
- **Edge**: Cross-compile with TVM for ARM targets
