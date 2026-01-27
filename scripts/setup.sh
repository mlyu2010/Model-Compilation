#!/bin/bash
# Setup script for Model Compilation project

set -e

echo "======================================"
echo "Model Compilation Project Setup"
echo "======================================"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/models data/binaries docs
echo "✓ Directories created"

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.py scripts/*.sh
echo "✓ Scripts are now executable"

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Build the Docker containers:"
echo "   make build"
echo ""
echo "2. Start the application:"
echo "   make up"
echo ""
echo "3. View logs:"
echo "   make logs"
echo ""
echo "4. Access the API:"
echo "   - Main API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "For more information, see USAGE.md"
echo ""
