# Dependencies Documentation

## Overview

This project has a modular dependency structure to handle optional ML compiler installations.

## Dependency Files

### requirements-base.txt
Core dependencies that are always required and readily available via PyPI:
- FastAPI & Uvicorn (web framework)
- PyTorch & TorchVision (ML framework)
- ONNX & ONNX Runtime (model interchange)
- Transformers (model loading)
- Testing & documentation tools

**Installation**:
```bash
pip install -r requirements-base.txt
```

### requirements.txt
Main requirements file that references base requirements and documents optional dependencies.

**Installation**:
```bash
pip install -r requirements.txt
```

## Optional Dependencies

### Apache TVM (ML Compiler)

**Why Optional**: TVM is not available on standard PyPI. It requires installation from:
- tlcpack wheels
- Conda-forge
- Source build

**Installation Options**:

1. **tlcpack (Recommended)**:
   ```bash
   pip install tlcpack-nightly -f https://tlcpack.ai/wheels
   ```

2. **Conda**:
   ```bash
   conda install -c conda-forge tvm
   ```

3. **From Source**:
   ```bash
   git clone --recursive https://github.com/apache/tvm.git
   cd tvm && mkdir build && cd build
   cmake .. && make -j4
   cd ../python && pip install -e .
   ```

**Fallback Behavior**: If TVM is not installed, attempting to use TVM compilation will raise an `ImportError` with installation instructions.

### PyTorch XLA (OpenXLA Compiler)

**Why Optional**: XLA has platform-specific requirements and can conflict with standard PyTorch installations.

**Installation Options**:

1. **For TPU (Google Cloud)**:
   ```bash
   pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html
   ```

2. **For CPU**:
   ```bash
   pip install torch_xla -f https://storage.googleapis.com/libtpu-releases/index.html
   ```

**Fallback Behavior**: If XLA is not installed, the system falls back to PyTorch JIT compilation with a warning.

## Dependency Resolution Strategy

### 1. Base Installation
Always installs successfully with standard PyPI packages.

### 2. Optional Compilation Support
TVM and XLA are detected at runtime:
```python
# TVM detection
try:
    import tvm
    TVM_AVAILABLE = True
except ImportError:
    TVM_AVAILABLE = False

# XLA detection
try:
    import torch_xla
    XLA_AVAILABLE = True
except ImportError:
    XLA_AVAILABLE = False
```

### 3. Graceful Degradation
- **TVM unavailable**: Raises clear error with installation instructions
- **XLA unavailable**: Falls back to PyTorch JIT with warning

## Version Compatibility

### Python
- **Required**: Python 3.13
- **Why**: Latest stable Python with performance improvements

### PyTorch
- **Version**: 2.10.0
- **Why**: Latest stable release with ONNX export improvements

### ONNX
- **Version**: 1.17.0
- **Compatible with**: PyTorch 2.10.0

### TVM
- **Version**: Latest from tlcpack-nightly
- **Alternative**: 0.17.0+ from conda-forge

### PyTorch XLA
- **Version**: Compatible with PyTorch 2.10.0
- **Note**: Platform-specific builds

## Docker Strategy

### Base Image
```dockerfile
FROM python:3.13-slim
```

### System Dependencies
Required for compilation support:
- build-essential
- cmake
- git
- llvm-14 & llvm-14-dev
- libopenblas-dev

### Python Dependencies
```dockerfile
# Install base requirements (always succeeds)
RUN pip install -r requirements-base.txt

# Try to install TVM (may fail, doesn't stop build)
RUN pip install tlcpack-nightly -f https://tlcpack.ai/wheels || \
    echo "Warning: TVM installation failed"
```

## Testing Dependencies

Included in requirements-base.txt:
- pytest (testing framework)
- pytest-asyncio (async test support)
- pytest-cov (coverage reporting)
- httpx (API testing)

## Documentation Dependencies

Included in requirements-base.txt:
- pdoc3 (API documentation generation)

## Development vs Production

### Development
- Install base requirements
- Optionally install TVM/XLA
- Use docker-compose.yml with hot-reload

### Production
- Install base requirements
- Install TVM for production workloads
- Use docker-compose.prod.yml with multiple workers
- Consider pre-built images with TVM

## Troubleshooting

### Import Errors

**TVM ImportError**:
```
ImportError: TVM is not installed. Install it with:
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```
**Solution**: Follow the installation instructions in the error message.

**XLA ImportError**:
```
Warning: PyTorch XLA is not installed. XLA features will use standard PyTorch JIT instead.
```
**Solution**: Optional - install XLA if needed, or continue with JIT fallback.

### Version Conflicts

**PyTorch Version Mismatch**:
- Ensure PyTorch, TorchVision, and XLA versions are compatible
- Check PyTorch compatibility matrix

**ONNX Compatibility**:
- ONNX 1.17.0 works with PyTorch 2.10.0
- Update both if needed

### Docker Build Issues

**TVM Installation Fails**:
- Expected behavior - build continues
- Install manually in running container:
  ```bash
  docker-compose exec model-compilation pip install tlcpack-nightly -f https://tlcpack.ai/wheels
  ```

**LLVM Not Found**:
- Check Dockerfile has llvm-14-dev installed
- May need to specify LLVM path for TVM build

## Recommended Installation Path

### For Full Features (TVM + XLA)
```bash
# 1. Install base requirements
pip install -r requirements-base.txt

# 2. Install TVM
pip install tlcpack-nightly -f https://tlcpack.ai/wheels

# 3. Install XLA (optional)
pip install torch_xla -f https://storage.googleapis.com/libtpu-releases/index.html
```

### For Basic Features (Export + API)
```bash
# Just install base requirements
pip install -r requirements-base.txt
```

### For Docker (Automatic)
```bash
# Docker handles dependencies automatically
docker-compose build
docker-compose up
```

## Future Improvements

1. **Conda Environment**:
   Create environment.yml for easier TVM installation via conda

2. **Pre-built Images**:
   Publish Docker images with TVM pre-installed

3. **Optional Extras**:
   ```bash
   pip install model-compilation[tvm]  # Installs with TVM
   pip install model-compilation[xla]  # Installs with XLA
   pip install model-compilation[full] # Installs everything
   ```

4. **Version Matrix**:
   Test and document compatible version combinations

## References

- PyTorch: https://pytorch.org/get-started/locally/
- TVM: https://tvm.apache.org/docs/install/
- PyTorch XLA: https://github.com/pytorch/xla
- ONNX: https://onnx.ai/
