# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9+
- PostgreSQL running on localhost:5432
- Anthropic API key (get free credits at https://console.anthropic.com)

### Step 1: Clone & Navigate
```bash
cd /Users/madgulasaikrishna/Documents/GitHub/movie-bot
```

### Step 2: Run Setup
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (handles venv, dependencies, and database)
./setup.sh
```

### Step 3: Configure Environment
```bash
# Edit .env with your settings
nano .env

# Add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### Step 4: Start Components (Open 3 Terminals)

**Terminal 1 - API Server:**
```bash
cd movie-bot
source venv/bin/activate
python -m api_server.main
# → API running at http://localhost:8000
```

**Terminal 2 - MCP Server:**
```bash
cd movie-bot
source venv/bin/activate
python -m mcp_server.server
```

**Terminal 3 - Agent:**
```bash
cd movie-bot
source venv/bin/activate
python agent/agent.py
```

### Step 5: Chat with Bot

```
Agent: "Welcome to Movie Bot! Type your query..."

You: "Find me action movies from 2020"
Agent: "Searching for action movies from 2020..."
[Results displayed]

You: "What movies are like Inception?"
Agent: "Getting recommendations similar to Inception..."
[Recommendations shown]

You: "Tell me about Avatar"
Agent: "Avatar is a 2009 sci-fi film directed by James Cameron..."
[Detailed information provided]
```

## 🎯 Common Commands

### Only Local Development

```bash
# Make scripts executable
chmod +x *.sh

# Run tests
./test.sh

# Check project structure
ls -la

# View logs
tail -f api.log
```

### Using CLI Tool

```bash
# Install dependencies
python cli.py install

# Setup database
python cli.py db

# Start individual services
python cli.py api    # API server
python cli.py mcp    # MCP server
python cli.py agent  # Agent
python cli.py test   # Run tests
```

### Docker (Optional)

```bash
# Make script executable
chmod +x start-docker.sh

# Start with Docker Compose
./start-docker.sh
```

## 📝 API Endpoints Quick Reference

### Movies
```bash
# List all movies
curl http://localhost:8000/movies/

# Get specific movie
curl http://localhost:8000/movies/603

# Search movies
curl -X POST http://localhost:8000/movies/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Inception", "limit": 5}'

# Get ratings for a movie
curl http://localhost:8000/movies/603/ratings

# Get keywords for a movie
curl http://localhost:8000/movies/603/keywords

# Get credits for a movie
curl http://localhost:8000/movies/603/credits
```

### Recommendations
```bash
# Get recommendations for a movie
curl http://localhost:8000/recommendations/603

# Get top rated movies
curl http://localhost:8000/recommendations/by-rating/avg

# Get trending movies
curl http://localhost:8000/recommendations/by-popularity/trending
```

### Utilities
```bash
# API documentation (interactive)
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

## 🔧 Troubleshooting

### Issue: "psycopg2" import error
```bash
# Install using brew (macOS)
brew install postgresql

# Or reinstall package
pip install --upgrade psycopg2-binary
```

### Issue: Port 8000 already in use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
export API_PORT=8001
```

### Issue: Database connection error
```bash
# Check if PostgreSQL is running
psql -h localhost -U postgres

# Start PostgreSQL (macOS)
brew services start postgresql

# Check PostgreSQL status
psql -l
```

### Issue: "ANTHROPIC_API_KEY not set"
```bash
# Make sure .env is in project root
cp .env.example .env

# Edit the file with your key
nano .env

# Add your key from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Try queries**: Ask the agent different movie questions
3. **Read docs**: Check [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Customize**: Modify tools, API endpoints, or agent prompt
5. **Scale up**: Add caching, authentication, or ML models

## 💡 Example Queries

```
"Find sci-fi movies with ratings above 8.0"
"Recommend movies similar to The Matrix"
"What was the highest budgeted movie made in 2015?"
"Show me movies with Tom Cruise"
"Get trending movies right now"
"Tell me about the cast of Interstellar"
"Find all movies from the Marvel universe"
"What movies have the keyword 'superhero'?"
```

## 🆘 Need Help?

1. Check [README.md](README.md) for full documentation
2. See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Review log files in project directory
4. Check database with: `psql -d movie_bot -c "SELECT COUNT(*) FROM movies;"`

## 📊 Project Structure

```
movie-bot/
├── agent/              # LLM Agent
├── api_server/         # FastAPI Server
│   ├── models/        # Data schemas
│   └── routes/        # API endpoints
├── mcp_server/        # MCP Tools Server
├── db/                # Database scripts
├── datasets/          # CSV data files
├── .env              # Configuration
├── requirements.txt   # Dependencies
├── README.md         # Full documentation
└── ARCHITECTURE.md   # System architecture
```

## ⚡ Performance Tips

1. **Enable query caching** - Reduces repeated queries
2. **Use pagination** - Limit=10 by default, adjust as needed
3. **Add more indexes** - For frequently filtered columns
4. **Monitor slow queries** - Use PostgreSQL slow query log
5. **Connection pooling** - Already enabled (NullPool for dev)

---

**Ready?** Start with Step 4 above! 🎬
