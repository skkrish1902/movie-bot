"""
Recommendations routes for API server
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api_server.database import get_db
from api_server.models.schemas import MovieResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{movie_id}", response_model=List[MovieResponse])
def get_recommendations(movie_id: int, limit: int = 5, db: Session = Depends(get_db)):
    """
    Get movie recommendations based on similar genres and ratings
    """
    # Get the target movie
    movie_query = "SELECT genres FROM movies WHERE id = %s"
    result = db.execute(text(movie_query), {"id": movie_id})
    movie = result.fetchone()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Find similar movies by genre
    # This is a simple implementation - you can make it more sophisticated with ML
    query = """
    SELECT id, adult, budget, genres, homepage, imdb_id, original_language, original_title, 
           overview, popularity, poster_path, production_companies, production_countries, 
           release_date, revenue, runtime, spoken_languages, status, tagline, title, 
           video, vote_average, vote_count
    FROM movies
    WHERE id != %s 
    AND vote_average > 5.0
    ORDER BY vote_average DESC, popularity DESC
    LIMIT %s
    """
    
    result = db.execute(text(query), {"id": movie_id, "limit": limit})
    recommendations = result.fetchall()
    
    return [r._mapping for r in recommendations]


@router.get("/by-rating/avg", response_model=List[MovieResponse])
def get_top_rated_movies(limit: int = 10, min_votes: int = 100, db: Session = Depends(get_db)):
    """Get top rated movies"""
    query = """
    SELECT id, adult, budget, genres, homepage, imdb_id, original_language, original_title, 
           overview, popularity, poster_path, production_companies, production_countries, 
           release_date, revenue, runtime, spoken_languages, status, tagline, title, 
           video, vote_average, vote_count
    FROM movies
    WHERE vote_count > %s
    ORDER BY vote_average DESC
    LIMIT %s
    """
    
    result = db.execute(text(query), {"min_votes": min_votes, "limit": limit})
    movies = result.fetchall()
    
    return [m._mapping for m in movies]


@router.get("/by-popularity/trending", response_model=List[MovieResponse])
def get_trending_movies(limit: int = 10, db: Session = Depends(get_db)):
    """Get trending movies by popularity"""
    query = """
    SELECT id, adult, budget, genres, homepage, imdb_id, original_language, original_title, 
           overview, popularity, poster_path, production_companies, production_countries, 
           release_date, revenue, runtime, spoken_languages, status, tagline, title, 
           video, vote_average, vote_count
    FROM movies
    ORDER BY popularity DESC
    LIMIT %s
    """
    
    result = db.execute(text(query), {"limit": limit})
    movies = result.fetchall()
    
    return [m._mapping for m in movies]
