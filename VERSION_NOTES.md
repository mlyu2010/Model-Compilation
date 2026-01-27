# Version Compatibility Notes

## Dependency Versioning Strategy

This project uses **flexible version constraints** for PyTorch and related libraries to avoid dependency conflicts while ensuring compatibility.

## Core Dependencies

### PyTorch & TorchVision

```python
torch>=2.9.0,<3.0.0
torchvision>=0.24.0,<1.0.0
```

**Why flexible versions?**
- PyTorch and TorchVision have tightly coupled dependencies
- Exact version pinning often causes conflicts
- Using `>=` allows pip to resolve compatible versions
- Using `<` ensures major version compatibility

**Tested with:**
- torch 2.9.1 + torchvision 0.24.1 ✅
- torch 2.10.0 + torchvision 0.25.0 ✅

### ONNX & ONNX Runtime

```python
onnx>=1.16.0
onnxruntime>=1.19.0
```

**Why flexible?**
- ONNX has good backward compatibility
- Newer versions add opset support
- Runtime versions track ONNX versions

**Minimum versions:**
- ONNX 1.16.0: Opset 16 support
- ONNX Runtime 1.19.0: Compatible with modern PyTorch

## Version Resolution

When you run `pip install -r requirements-base.txt`, pip will:

1. Resolve the latest compatible versions within constraints
2. Ensure PyTorch and TorchVision are compatible
3. Match ONNX Runtime with installed PyTorch

**Example resolution** (as of 2026-01-26):
```
torch==2.10.0
torchvision==0.25.0
onnx==1.19.0
onnxruntime==1.23.2
```

## Platform-Specific Versions

### macOS (Apple Silicon)

PyTorch provides ARM64-optimized wheels:
```bash
# Automatically selects ARM64 wheels
pip install -r requirements-base.txt
```

### macOS (Intel)

Standard x86_64 wheels are used:
```bash
pip install -r requirements-base.txt
```

### Linux

CUDA support requires PyTorch with CUDA:
```bash
# CPU-only (default)
pip install -r requirements-base.txt

# With CUDA 11.8
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# With CUDA 12.1
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Windows

```bash
# CPU-only
pip install -r requirements-base.txt

# With CUDA (see PyTorch website for current commands)
# https://pytorch.org/get-started/locally/
```

## Checking Installed Versions

```python
import torch
import torchvision
import onnx
import onnxruntime

print(f"PyTorch: {torch.__version__}")
print(f"TorchVision: {torchvision.__version__}")
print(f"ONNX: {onnx.__version__}")
print(f"ONNX Runtime: {onnxruntime.__version__}")
```

## Compatibility Matrix

| PyTorch | TorchVision | ONNX | ONNX RT | Status |
|---------|-------------|------|---------|--------|
| 2.9.1 | 0.24.1 | 1.16+ | 1.19+ | ✅ Tested |
| 2.10.0 | 0.25.0 | 1.19+ | 1.23+ | ✅ Tested |
| 2.11.x | 0.26.x | 1.19+ | 1.23+ | ⚠️ Not yet tested |

## Troubleshooting Version Issues

### Dependency Conflict Error

```
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io...
```

**Solution 1:** Upgrade pip
```bash
pip install --upgrade pip
pip install -r requirements-base.txt
```

**Solution 2:** Use clean environment
```bash
python3.13 -m venv .venv-clean
source .venv-clean/bin/activate
pip install --upgrade pip
pip install -r requirements-base.txt
```

**Solution 3:** Install PyTorch first
```bash
pip install torch torchvision
pip install -r requirements-base.txt
```

### Version Too Old

```
ERROR: Could not find a version that satisfies the requirement torch>=2.9.0
```

**Solution:** Upgrade pip and check Python version
```bash
# Requires Python 3.9+
python --version

# Upgrade pip
pip install --upgrade pip
```

### ONNX/PyTorch Incompatibility

```
RuntimeError: Unsupported ONNX opset version
```

**Solution:** Export with specific opset
```python
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=16  # Supported by ONNX 1.16+
)
```

## Optional Dependencies

### TVM

TVM is **version-independent** from PyTorch:
```bash
pip install tlcpack-nightly -f https://tlcpack.ai/wheels
```

**Compatibility:** Works with any PyTorch version

### PyTorch XLA

XLA requires **exact PyTorch version match**:
```bash
# Must match your PyTorch version exactly
pip show torch  # Check installed version
pip install torch_xla==2.x.x  # Match the version
```

**Platform:** Linux + TPU only

## Pinning Versions (Not Recommended)

If you need exact versions for reproducibility:

```bash
# Generate lockfile
pip freeze > requirements.lock

# Install from lockfile
pip install -r requirements.lock
```

**Downsides:**
- May not work across platforms
- Breaks on version conflicts
- Harder to upgrade

## Recommended Approach

**Development:**
```bash
# Use flexible versions
pip install -r requirements-base.txt
```

**Production:**
```bash
# Generate lockfile from working environment
pip freeze > requirements.lock

# Test thoroughly
pytest

# Deploy with lockfile
pip install -r requirements.lock
```

## Version Update Policy

### When to Update

- Security vulnerabilities
- New features needed
- Bug fixes
- Better performance

### How to Update

1. Test in development first
2. Update version constraints if needed
3. Run full test suite
4. Update VERSION_NOTES.md
5. Generate new lockfile for production

### Version Constraint Guidelines

- **Exact (`==`)**: Use only for known conflicts (e.g., fastapi==0.115.0)
- **Compatible (`>=,<`)**: Use for PyTorch, ONNX (e.g., torch>=2.9.0,<3.0.0)
- **Minimum (`>=`)**: Use for stable libraries (e.g., numpy>=1.26.0)

## Testing Version Compatibility

```bash
# Test current environment
pytest

# Test with minimum versions
pip install torch==2.9.0 torchvision==0.24.0 onnx==1.16.0
pytest

# Test with latest versions
pip install --upgrade torch torchvision onnx onnxruntime
pytest
```

## Docker Version Strategy

Docker uses the **same flexible requirements**:
```dockerfile
RUN pip install -r requirements-base.txt
```

**Benefits:**
- Always gets latest compatible versions
- Reduces build failures
- Better security (newer versions)

**For reproducibility:**
```dockerfile
# Option 1: Use lockfile
COPY requirements.lock .
RUN pip install -r requirements.lock

# Option 2: Pin base image date
FROM python:3.13-slim-20260126
```

## Summary

✅ **Use flexible version constraints** - Let pip resolve compatible versions
✅ **Test across version range** - Ensure compatibility with min and max
✅ **Update regularly** - Get security fixes and improvements
✅ **Lock for production** - Use pip freeze for reproducible deploys
✅ **Document changes** - Update this file when changing constraints

---

**Last Updated:** 2026-01-26
**Tested with:** Python 3.13, torch 2.9.1-2.10.0, torchvision 0.24.1-0.25.0
