"""
Main API server application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from api_server.routes import movies, recommendations

# Create FastAPI app
app = FastAPI(
    title="Movie Bot API",
    description="API server for movie data and recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(movies.router)
app.include_router(recommendations.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Movie Bot API Server",
        "version": "1.0.0",
        "endpoints": {
            "movies": "/movies",
            "recommendations": "/recommendations",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
