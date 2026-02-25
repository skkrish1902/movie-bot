"""
MCP Server for Movie Bot
Provides tools for interacting with the movie database
"""
import json
import os
from typing import Any
from mcp.server.session import SessionManager
from mcp.server import Server
from mcp.types import TextContent, Tool
import httpx

# Initialize MCP Server
server = Server("movie-bot-mcp")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
HTTP_CLIENT = httpx.AsyncClient(base_url=API_BASE_URL)

# Tool definitions
TOOLS = [
    {
        "name": "search_movies",
        "description": "Search for movies by title",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Movie title or keyword to search for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_movie_details",
        "description": "Get detailed information about a specific movie",
        "inputSchema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The TMDB ID of the movie"
                }
            },
            "required": ["movie_id"]
        }
    },
    {
        "name": "get_recommendations",
        "description": "Get movie recommendations based on a specific movie",
        "inputSchema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The TMDB ID of the movie to get recommendations for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of recommendations",
                    "default": 5
                }
            },
            "required": ["movie_id"]
        }
    },
    {
        "name": "get_top_rated",
        "description": "Get top rated movies",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of movies to return",
                    "default": 10
                },
                "min_votes": {
                    "type": "integer",
                    "description": "Minimum number of votes required",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "get_trending",
        "description": "Get trending movies by popularity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of movies to return",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "get_movie_ratings",
        "description": "Get all ratings for a specific movie",
        "inputSchema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The TMDB ID of the movie"
                }
            },
            "required": ["movie_id"]
        }
    },
    {
        "name": "get_movie_keywords",
        "description": "Get keywords associated with a movie",
        "inputSchema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The TMDB ID of the movie"
                }
            },
            "required": ["movie_id"]
        }
    },
    {
        "name": "get_movie_credits",
        "description": "Get cast and crew information for a movie",
        "inputSchema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The TMDB ID of the movie"
                }
            },
            "required": ["movie_id"]
        }
    }
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"]
        )
        for tool in TOOLS
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Any:
    """Execute a tool"""
    try:
        if name == "search_movies":
            response = await HTTP_CLIENT.post(
                "/movies/search",
                json={
                    "query": arguments["query"],
                    "limit": arguments.get("limit", 10)
                }
            )
            return json.dumps(response.json())
        
        elif name == "get_movie_details":
            response = await HTTP_CLIENT.get(
                f"/movies/{arguments['movie_id']}"
            )
            if response.status_code == 404:
                return "Movie not found"
            return json.dumps(response.json())
        
        elif name == "get_recommendations":
            response = await HTTP_CLIENT.get(
                f"/recommendations/{arguments['movie_id']}",
                params={"limit": arguments.get("limit", 5)}
            )
            if response.status_code == 404:
                return "Movie not found"
            return json.dumps(response.json())
        
        elif name == "get_top_rated":
            response = await HTTP_CLIENT.get(
                "/recommendations/by-rating/avg",
                params={
                    "limit": arguments.get("limit", 10),
                    "min_votes": arguments.get("min_votes", 100)
                }
            )
            return json.dumps(response.json())
        
        elif name == "get_trending":
            response = await HTTP_CLIENT.get(
                "/recommendations/by-popularity/trending",
                params={"limit": arguments.get("limit", 10)}
            )
            return json.dumps(response.json())
        
        elif name == "get_movie_ratings":
            response = await HTTP_CLIENT.get(
                f"/movies/{arguments['movie_id']}/ratings"
            )
            if response.status_code == 404:
                return "Ratings not found"
            return json.dumps(response.json())
        
        elif name == "get_movie_keywords":
            response = await HTTP_CLIENT.get(
                f"/movies/{arguments['movie_id']}/keywords"
            )
            if response.status_code == 404:
                return "Keywords not found"
            return json.dumps(response.json())
        
        elif name == "get_movie_credits":
            response = await HTTP_CLIENT.get(
                f"/movies/{arguments['movie_id']}/credits"
            )
            if response.status_code == 404:
                return "Credits not found"
            return json.dumps(response.json())
        
        else:
            return f"Unknown tool: {name}"
    
    except Exception as e:
        return f"Error calling tool {name}: {str(e)}"


async def run():
    """Run the MCP server"""
    async with server:
        print("Movie Bot MCP Server running on stdio")
        await server.wait()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
