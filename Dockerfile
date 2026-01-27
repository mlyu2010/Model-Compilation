FROM python:3.13-slim

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

# Try to install TVM from tlcpack (optional, may fail)
RUN pip install --no-cache-dir tlcpack-nightly -f https://tlcpack.ai/wheels || \
    echo "Warning: TVM installation failed. TVM features will not be available."

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/models data/binaries

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
