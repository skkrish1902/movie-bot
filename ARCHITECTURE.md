# Movie Bot Architecture & Integration Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                      (Interactive Agent)                         │
└────────────┬────────────────────────────────────────────────────┘
             │ User queries
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Agent (Claude 3)                         │
│                  - Query understanding                           │
│                  - Response generation                           │
│                  - Tool orchestration                            │
└────────────┬────────────────────────────────────────────────────┘
             │ Tool calls (via MCP)
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCP Server (Tool Bridge)                            │
│         - search_movies                                          │
│         - get_movie_details                                      │
│         - get_recommendations                                    │
│         - get_ratings/keywords/credits                           │
└────────────┬────────────────────────────────────────────────────┘
             │ REST API calls
             ▼
┌─────────────────────────────────────────────────────────────────┐
│            FastAPI Server (Movie Data API)                       │
│         - /movies endpoints                                      │
│         - /recommendations endpoints                             │
│         - Search & filtering                                     │
└────────────┬────────────────────────────────────────────────────┘
             │ SQL queries
             ▼
┌─────────────────────────────────────────────────────────────────┐
│          PostgreSQL Database (movie_bot)                         │
│         - movies table                                           │
│         - credits table                                          │
│         - keywords table                                         │
│         - ratings table                                          │
│         - links table                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Query Flow
```
User types query
        ↓
Agent receives query
        ↓
Claude LLM processes query
        ↓
Determines which tools to use
        ↓
Calls MCP tools with parameters
        ↓
MCP server makes REST API calls
        ↓
API server queries database
        ↓
Results returned through chain
        ↓
Claude formats final response
        ↓
Response displayed to user
```

### 2. Data Loading Flow
```
CSV files
    ↓
load_data.py (Python script)
    ↓
Data validation & transformation
    ↓
Create PostgreSQL tables
    ↓
Bulk insert records
    ↓
Create indexes
    ↓
Database ready for queries
```

### 3. API Request Flow
```
HTTP request to API server
        ↓
FastAPI routes handler
        ↓
Query parameters processing
        ↓
SQLAlchemy generates SQL
        ↓
PostgreSQL executes query
        ↓
Results serialized to JSON
        ↓
HTTP response returned
```

## Component Interaction

### Agent ↔ MCP Server
- **Protocol**: Model Context Protocol (stdio-based)
- **Tool Definitions**: JSON schema for each tool
- **Communication**: Async/await with tool execution
- **Error Handling**: Tool results include error information

### MCP Server ↔ API Server
- **Protocol**: HTTP/RESTful
- **Format**: JSON request/response
- **Authentication**: None (localhost only, can be added)
- **Timeout**: 30 seconds per request

### API Server ↔ Database
- **Driver**: psycopg2/SQLAlchemy
- **Connection Pool**: Managed by SQLAlchemy
- **Query Type**: Raw SQL with parameterized queries
- **Transactions**: Auto-commit for read operations

## Tool Ecosystem

The MCP Server provides 8 main tools:

### Search & Browse
- `search_movies`: Full-text search on title
- `get_movie_details`: Retrieve all data for a movie
- `get_movie_keywords`: Get associated keywords
- `get_movie_credits`: Get cast and crew

### Recommendations
- `get_recommendations`: Suggest similar movies
- `get_top_rated`: High-quality movies
- `get_trending`: Popular movies

### Reviews
- `get_movie_ratings`: User ratings data

## Database Schema Details

### Movies Table
```sql
id (BIGINT, PRIMARY KEY)
title (VARCHAR)
overview (TEXT)
release_date (DATE)
vote_average (FLOAT)
vote_count (INT)
budget (BIGINT)
revenue (BIGINT)
runtime (FLOAT)
popularity (FLOAT)
genres (JSONB)
production_companies (JSONB)
production_countries (JSONB)
spoken_languages (JSONB)
... additional fields
```

### Credits Table
```sql
id (BIGINT, PRIMARY KEY)
movie_id (BIGINT, FOREIGN KEY → movies.id)
cast (JSONB)  -- Array of actor objects
crew (JSONB)  -- Array of crew member objects
```

### Keywords Table
```sql
id (BIGINT, PRIMARY KEY)
movie_id (BIGINT, FOREIGN KEY → movies.id)
keywords (JSONB)  -- Array of keyword objects
```

### Ratings Table
```sql
id (SERIAL, PRIMARY KEY)
user_id (INT)
movie_id (INT)
rating (FLOAT)
timestamp (BIGINT)
```

### Links Table
```sql
movie_id (INT, PRIMARY KEY)
imdb_id (VARCHAR)
tmdb_id (BIGINT, FOREIGN KEY → movies.id)
```

## Integration Points

### 1. Adding New Tools to MCP Server
```python
# In mcp_server/server.py

@server.list_tools()
async def list_tools():
    # Add new tool definition
    return [...TOOLS, new_tool_definition]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "new_tool_name":
        # Implementation
        pass
```

### 2. Adding New API Endpoints
```python
# In api_server/routes/new_route.py

@router.get("/endpoint")
def endpoint(param: str, db: Session = Depends(get_db)):
    # Query database
    # Return response
    pass

# In api_server/main.py
app.include_router(new_route.router)
```

### 3. Extending the Agent
```python
# In agent/agent.py

async def new_skill(self, param: str) -> str:
    """New agent capability"""
    # Can use tools or call Claude directly
    pass
```

## Performance Optimization

### Database Indexes
```sql
-- Movies
CREATE INDEX idx_movies_title ON movies(title)
CREATE INDEX idx_movies_release_date ON movies(release_date)

-- Ratings
CREATE INDEX idx_ratings_user_id ON ratings(user_id)
CREATE INDEX idx_ratings_movie_id ON ratings(movie_id)

-- Foreign keys
CREATE INDEX idx_keywords_movie_id ON keywords(movie_id)
CREATE INDEX idx_credits_movie_id ON credits(movie_id)
```

### Query Optimization
- Use LIMIT for pagination
- Filter before sorting
- EXPLAIN ANALYZE for slow queries
- Connection pooling enabled

### Caching (Future)
- API response caching (Redis)
- Tool result caching
- AI response caching for similar queries

## Security Considerations

### Current State
- ✅ SQL injection protected (parameterized queries)
- ✅ Input validation (Pydantic models)
- ✅ Localhost only connections

### Future Enhancements
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] HTTPS/TLS
- [ ] API key management
- [ ] Input sanitization
- [ ] Query timeout limits

## Deployment Scenarios

### Development
```bash
# Local setup with all components
source venv/bin/activate
python db/load_data.py        # Terminal 1
python -m api_server.main      # Terminal 2
python -m mcp_server.server    # Terminal 3
python agent/agent.py          # Terminal 4
```

### Docker Compose
```bash
docker-compose up
# PostgreSQL + API Server in containers
# Agent runs locally
```

### Production
```bash
# Kubernetes/Cloud deployment
# PostgreSQL managed service
# API as microservice
# MCP as sidecar/separate service
# Agent as service
```

## Monitoring & Logging

### Recommended Tools
- **Logging**: Python logging + ELK stack
- **Monitoring**: Prometheus + Grafana
- **Tracing**: Jaeger/Zipkin
- **Metrics**: StatsD/Prometheus client

### Key Metrics
- API response time
- Database query time
- Tool execution time
- Error rates
- Cache hit rates

## Testing Strategy

### Unit Tests
- Individual tool tests
- Database operations
- API endpoints

### Integration Tests
- Agent → MCP → API → DB
- Tool execution with real data
- Error scenarios

### Load Tests
- API server performance
- Database connection pool
- Concurrent requests

## Example Flows

### Flow 1: Movie Search
```
User: "Find me action movies"
  ↓
Agent: Calls search_movies("action")
  ↓
MCP: Calls POST /movies/search
  ↓
API: Queries movies WHERE genres LIKE '%action%'
  ↓
DB: Returns matching movies
  ↓
Agent: Formats response with titles, ratings, etc.
  ↓
User: Sees list of action movies
```

### Flow 2: Get Recommendations
```
User: "I like Inception, recommend similar movies"
  ↓
Agent: Extracts movie name, queries get_recommendations(603)
  ↓
MCP: Calls GET /recommendations/603
  ↓
API: Finds similar movies by genre/rating
  ↓
DB: Returns 5 top recommendations
  ↓
Agent: Enhances with brief descriptions
  ↓
User: Sees personalized recommendations
```

## Troubleshooting Common Issues

### Agent Can't Find Tools
- [ ] MCP server running?
- [ ] API server responding?
- [ ] ANTHROPIC_API_KEY set?

### Database Errors
- [ ] PostgreSQL running?
- [ ] Correct credentials in .env?
- [ ] Database created?

### API Timeouts
- [ ] Large result sets?
- [ ] Missing indexes?
- [ ] Slow queries (use EXPLAIN)?
