#!/bin/bash

# Movie Bot Setup Script
# This script sets up the complete movie chatbot system

set -e

echo "🎬 Movie Bot Setup Script"
echo "=========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed locally"
    echo "Make sure PostgreSQL server is running on localhost:5432"
fi

# Create virtual environment
echo ""
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Setup database
echo ""
echo "🗄️  Setting up database..."
python db/load_data.py

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your Anthropic API key"
echo "2. Start API server: python -m api_server.main"
echo "3. Start MCP server: python -m mcp_server.server"
echo "4. Start agent: python agent/agent.py"
echo ""
