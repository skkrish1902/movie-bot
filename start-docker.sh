#!/bin/bash

# Docker startup script for production deployment

set -e

PROJECT_NAME="movie-bot"

echo "🎬 Starting Movie Bot with Docker Compose"
echo "========================================"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
else
    echo "❌ .env file not found. Please copy .env.example to .env and configure"
    exit 1
fi

echo "🔨 Building images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Logs:"
docker-compose logs -f

