#!/bin/bash
# Quick test script for Docker setup

set -e

echo "🐳 Testing utube-transcript Docker Setup"
echo "========================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✓ Docker is installed"

# Check docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi
echo "✓ docker-compose is installed"

# Check .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, creating from .env.example..."
    cp .env.example .env
    echo "   Please edit .env and add your OPENAI_API_KEY"
fi
echo "✓ .env file exists"

# Check output directory
if [ ! -d output ]; then
    echo "Creating output directory..."
    mkdir -p output
fi
echo "✓ output directory exists"

# Build CPU image
echo ""
echo "Building CPU image..."
docker-compose build utube-transcript-cpu

echo ""
echo "✅ Docker setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Run: docker-compose --profile cpu up utube-transcript-cpu"
echo ""
echo "For GPU support:"
echo "1. Ensure nvidia-docker is installed"
echo "2. Build GPU image: docker-compose build utube-transcript-gpu"
echo "3. Run: docker-compose --profile gpu up utube-transcript-gpu"
echo ""
echo "See DOCKER.md for more usage examples"
