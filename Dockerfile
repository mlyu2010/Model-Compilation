FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Note: Using latest LLVM available in Debian repos (llvm-14 not available in Trixie)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    llvm \
    llvm-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-base.txt requirements.txt ./

# Install base Python dependencies
RUN pip install --no-cache-dir -r requirements-base.txt

# Apache TVM installation (optional)
# Note: TVM is not installed by default due to platform compatibility issues:
# - apache-tvm requires numpy<=1.23 which lacks ARM64 wheels
# - Building numpy from source often fails on ARM64/Apple Silicon
# - TVM features will be unavailable, but the application will still run
# To enable TVM on x86_64 Linux, uncomment the following line:
# RUN pip install --no-cache-dir apache-tvm
RUN echo "Note: TVM is not installed. TVM compilation features will be unavailable."

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/models data/binaries

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
