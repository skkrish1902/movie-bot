#!/bin/bash

# Development startup script for movie-bot
# Starts all components in separate tmux windows

set -e

PROJECT_NAME="movie-bot"
VENV_PATH="venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🎬 Movie Bot Development Startup${NC}"
echo "===================================="

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}tmux not found. Installing required packages...${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y tmux
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install tmux
    fi
fi

# Activate virtual environment
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

# Install dependencies if needed
pip install -q -r requirements.txt

# Create a new tmux session
if tmux has-session -t "$PROJECT_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Killing existing session...${NC}"
    tmux kill-session -t "$PROJECT_NAME"
fi

echo -e "${GREEN}Starting tmux session: $PROJECT_NAME${NC}"
tmux new-session -d -s "$PROJECT_NAME" -x 140 -y 50

# Window 1: Database setup (if needed) + Database logs
echo -e "${GREEN}[1/4] Setting up database...${NC}"
tmux send-keys -t "$PROJECT_NAME" "source $VENV_PATH/bin/activate && python db/load_data.py" Enter

# Window 2: API Server
echo -e "${GREEN}[2/4] Starting API Server...${NC}"
tmux new-window -t "$PROJECT_NAME" -n "api"
tmux send-keys -t "$PROJECT_NAME:api" "source $VENV_PATH/bin/activate && python -m api_server.main" Enter
sleep 2

# Window 3: MCP Server
echo -e "${GREEN}[3/4] Starting MCP Server...${NC}"
tmux new-window -t "$PROJECT_NAME" -n "mcp"
tmux send-keys -t "$PROJECT_NAME:mcp" "source $VENV_PATH/bin/activate && python -m mcp_server.server" Enter
sleep 1

# Window 4: Agent
echo -e "${GREEN}[4/4] Starting Agent...${NC}"
tmux new-window -t "$PROJECT_NAME" -n "agent"
tmux send-keys -t "$PROJECT_NAME:agent" "source $VENV_PATH/bin/activate && python agent/agent.py" Enter

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📋 Tmux session: $PROJECT_NAME"
echo "   - Window 0: Database setup"
echo "   - Window 1 (api): API server (http://localhost:8000)"
echo "   - Window 2 (mcp): MCP server"
echo "   - Window 3 (agent): Interactive agent"
echo ""
echo "🎮 Commands:"
echo "   tmux attach -t movie-bot          # Attach to session"
echo "   tmux select-window -t movie-bot:0 # Go to window 0"
echo "   tmux kill-session -t movie-bot    # Kill session"
echo ""
echo "🌐 API Documentation: http://localhost:8000/docs"
echo ""
