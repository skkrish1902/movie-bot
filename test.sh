#!/bin/bash

# Quick test script to verify all components are working

set -e

VENV_PATH="venv"

echo "🧪 Movie Bot Component Test"
echo "============================"

# Activate virtual environment
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Test 1: Check imports
echo ""
echo "✓ Test 1: Checking Python imports..."
python3 -c "
import fastapi
import sqlalchemy
import pandas
import anthropic
print('  All imports successful!')
"

# Test 2: Database connection
echo ""
echo "✓ Test 2: Testing database connection..."
python3 -c "
import os
import psycopg2
from sqlalchemy import create_engine, text

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print('  Database connection successful!')
    conn.close()
except Exception as e:
    print(f'  ⚠️  Database connection failed: {e}')
    print('  Make sure PostgreSQL is running on localhost:5432')
"

# Test 3: API endpoints
echo ""
echo "✓ Test 3: Checking API server status..."
python3 -c "
import httpx
import time

try:
    response = httpx.get('http://localhost:8000/health', timeout=2)
    print('  API server is healthy!')
except Exception as e:
    print('  ⚠️  API server is not running')
    print('  Start it with: python -m api_server.main')
"

# Test 4: Check environment variables
echo ""
echo "✓ Test 4: Checking environment variables..."
python3 -c "
import os

vars_to_check = [
    'DB_HOST',
    'DB_PORT', 
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME',
    'ANTHROPIC_API_KEY'
]

for var in vars_to_check:
    value = os.getenv(var, 'NOT SET')
    if var == 'ANTHROPIC_API_KEY':
        print(f'  {var}: {value[:10]}...' if len(value) > 10 else f'  {var}: {value}')
    else:
        print(f'  {var}: {value}')
"

echo ""
echo "✅ Basic tests completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Start API server: python -m api_server.main"
echo "   2. Start MCP server: python -m mcp_server.server"
echo "   3. Start agent: python agent/agent.py"
echo ""
