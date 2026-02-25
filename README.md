# Movie Bot Project

A movie chatbot system with LLM integration, MCP server, and API backend.

## Architecture

```
movie-bot/
├── agent/                 # LLM Agent for interacting with Claude
├── api_server/            # FastAPI server for movie data
├── mcp_server/            # Model Context Protocol server with tools
├── db/                    # Database setup and management
├── datasets/              # Movie datasets (CSV files)
└── venv/                  # Python virtual environment
```

## Components

### 1. Database Layer (`db/`)
- **load_data.py**: Script to load CSV data into PostgreSQL
- Handles data transformation and validation
- Creates indexes for optimal query performance

### 2. API Server (`api_server/`)
- FastAPI application serving movie data
- RESTful endpoints for movies, ratings, credits, keywords
- Recommendation engine
- CORS enabled for cross-origin requests

**Endpoints:**
- `GET /movies/` - List movies with pagination
- `GET /movies/{movie_id}` - Get movie details
- `POST /movies/search` - Search movies by title
- `GET /movies/{movie_id}/ratings` - Get movie ratings
- `GET /movies/{movie_id}/keywords` - Get movie keywords
- `GET /movies/{movie_id}/credits` - Get cast and crew
- `GET /recommendations/{movie_id}` - Get recommendations
- `GET /recommendations/by-rating/avg` - Top rated movies
- `GET /recommendations/by-popularity/trending` - Trending movies

### 3. MCP Server (`mcp_server/`)
- Model Context Protocol server implementation
- Provides tools for LLM integration:
  - `search_movies` - Search for movies
  - `get_movie_details` - Get detailed movie info
  - `get_recommendations` - Get movie recommendations
  - `get_top_rated` - Top rated movies
  - `get_trending` - Trending movies
  - `get_movie_ratings` - Get ratings
  - `get_movie_keywords` - Get keywords
  - `get_movie_credits` - Get cast/crew

### 4. LLM Agent (`agent/`)
- Main agent for user interaction
- Connects to Claude LLM via Anthropic API
- Uses MCP tools to fetch data
- Provides natural language interface to movie database
- Commands:
  - Natural movie queries
  - Summarization of text
  - Text improvement

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL server running on localhost:5432
- Anthropic API key

### Installation

1. **Clone the repository and navigate to the directory:**
   ```bash
   cd movie-bot
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Manually create a `.env` file** (or update the generated one):
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

### Manual Setup (if setup.sh doesn't work)

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database:**
   ```bash
   python db/load_data.py
   ```

## Running the System

### 1. Start the API Server
```bash
source venv/bin/activate
python -m api_server.main
```
The API will be available at `http://localhost:8000`
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Start the MCP Server
```bash
source venv/bin/activate
python -m mcp_server.server
```

### 3. Start the Agent
In a separate terminal:
```bash
source venv/bin/activate
python agent/agent.py
```

This provides an interactive chat interface with the movie chatbot.

## Configuration

### Environment Variables (.env)

- `DB_HOST` - PostgreSQL host (default: localhost)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_USER` - PostgreSQL user (default: postgres)
- `DB_PASSWORD` - PostgreSQL password (default: postgres)
- `DB_NAME` - Database name (default: movie_bot)
- `API_BASE_URL` - API server URL (default: http://localhost:8000)
- `ANTHROPIC_API_KEY` - Your Anthropic API key (REQUIRED)
- `MODEL` - Claude model to use (default: claude-3-5-sonnet-20241022)
- `CORS_ORIGINS` - CORS allowed origins (default: *)

## Database Schema

### Movies Table
- id, title, overview, release_date, budget, revenue, runtime, vote_average, vote_count, genres, etc.

### Credits Table
- id, cast (JSONB), crew (JSONB), movie_id

### Keywords Table
- id, keywords (JSONB), movie_id

### Ratings Table
- user_id, movie_id, rating, timestamp

### Links Table
- movie_id, imdb_id, tmdb_id

## Usage Examples

### Search for movies
```
Agent: "Find me action movies"
```

### Get recommendations
```
Agent: "I like Inception, can you recommend similar movies?"
```

### Get movie details
```
Agent: "Tell me about Avatar"
```

### Get top-rated movies
```
Agent: "What are the best rated movies?"
```

## API Examples

```bash
# Search movies
curl -X POST http://localhost:8000/movies/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Inception", "limit": 5}'

# Get movie details
curl http://localhost:8000/movies/603

# Get recommendations
curl http://localhost:8000/recommendations/603

# Get top-rated movies
curl http://localhost:8000/recommendations/by-rating/avg?limit=10
```

## Datasets

The project uses the following datasets:
- **movies_metadata.csv** - Movie information (title, budget, genres, etc.)
- **credits.csv** - Cast and crew information
- **keywords.csv** - Movie keywords/tags
- **links.csv** - IMDB and TMDB IDs mapping
- **ratings.csv** - User ratings
- **ratings_small.csv** - Subset of ratings for quick testing
- **links_small.csv** - Subset of links for quick testing

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL is running: `psql postgres`
- Check credentials in `.env` file
- Verify DB_NAME exists: `psql -l`

### API server won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify database is running and accessible

### MCP server connection errors
- Ensure API server is running first
- Check `API_BASE_URL` in `.env` is correct

### Agent not responding
- Verify Anthropic API key is set in `.env`
- Check if API server and MCP server are running
- Look at logs for detailed error messages

## Development

### Project Structure
```
movie-bot/
├── api_server/
│   ├── main.py              # FastAPI app
│   ├── database.py          # DB configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── routes/
│       ├── movies.py        # Movie endpoints
│       └── recommendations.py # Recommendation endpoints
├── mcp_server/
│   ├── server.py            # MCP server implementation
│   └── tools/               # Tool definitions
├── agent/
│   └── agent.py             # LLM agent
├── db/
│   └── load_data.py         # Data loading script
├── datasets/                # CSV data files
├── requirements.txt         # Python dependencies
├── .env                     # Configuration
└── README.md               # This file
```

## Future Enhancements

- [ ] Implement collaborative filtering recommendations
- [ ] Add caching layer (Redis)
- [ ] Implement user authentication
- [ ] Add more sophisticated NLP analysis
- [ ] Create frontend web interface
- [ ] Add streaming responses for long operations
- [ ] Implement vector search with embeddings
- [ ] Add movie review sentiment analysis

## License

This project is open source and available under the MIT License.
