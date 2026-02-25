"""
Movie routes for API server
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api_server.database import get_db
from api_server.models.schemas import (
    MovieResponse, MovieDetailResponse, SearchResponse,
    RatingResponse, KeywordResponse, CreditResponse, SearchRequest
)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=List[MovieResponse])
def get_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get a list of movies with pagination"""
    query = "SELECT id, adult, budget, genres, homepage, imdb_id, original_language, original_title, overview, popularity, poster_path, production_companies, production_countries, release_date, revenue, runtime, spoken_languages, status, tagline, title, video, vote_average, vote_count FROM movies LIMIT %s OFFSET %s"
    result = db.execute(text(query), {"limit": limit, "offset": skip})
    movies = result.fetchall()
    return movies


@router.get("/{movie_id}", response_model=MovieDetailResponse)
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific movie"""
    # Get movie
    movie_query = "SELECT id, adult, budget, genres, homepage, imdb_id, original_language, original_title, overview, popularity, poster_path, production_companies, production_countries, release_date, revenue, runtime, spoken_languages, status, tagline, title, video, vote_average, vote_count FROM movies WHERE id = %s"
    result = db.execute(text(movie_query), {"id": movie_id})
    movie = result.fetchone()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Get credits
    credits_query = "SELECT id, cast, crew FROM credits WHERE movie_id = %s"
    credits_result = db.execute(text(credits_query), {"id": movie_id})
    credits = credits_result.fetchone()
    
    # Get keywords
    keywords_query = "SELECT id, keywords FROM keywords WHERE movie_id = %s"
    keywords_result = db.execute(text(keywords_query), {"id": movie_id})
    keywords = keywords_result.fetchone()
    
    # Get ratings
    ratings_query = "SELECT user_id, movie_id, rating, timestamp FROM ratings WHERE movie_id = %s LIMIT 100"
    ratings_result = db.execute(text(ratings_query), {"id": movie_id})
    ratings = ratings_result.fetchall()
    
    return {
        **movie._mapping,
        "credits": credits._mapping if credits else None,
        "keywords": keywords._mapping if keywords else None,
        "ratings": [r._mapping for r in ratings]
    }


@router.post("/search", response_model=SearchResponse)
def search_movies(search: SearchRequest, db: Session = Depends(get_db)):
    """Search for movies by title"""
    query = """
    SELECT id, adult, budget, genres, homepage, imdb_id, original_language, original_title, 
           overview, popularity, poster_path, production_companies, production_countries, 
           release_date, revenue, runtime, spoken_languages, status, tagline, title, 
           video, vote_average, vote_count 
    FROM movies 
    WHERE title ILIKE %s 
    ORDER BY popularity DESC 
    LIMIT %s
    """
    search_term = f"%{search.query}%"
    result = db.execute(text(query), {"query": search_term, "limit": search.limit})
    movies = result.fetchall()
    
    return {
        "results": [m._mapping for m in movies],
        "total_count": len(movies)
    }


@router.get("/{movie_id}/ratings", response_model=List[RatingResponse])
def get_movie_ratings(movie_id: int, db: Session = Depends(get_db)):
    """Get all ratings for a movie"""
    query = "SELECT user_id, movie_id, rating, timestamp FROM ratings WHERE movie_id = %s"
    result = db.execute(text(query), {"id": movie_id})
    ratings = result.fetchall()
    return [r._mapping for r in ratings]


@router.get("/{movie_id}/keywords", response_model=KeywordResponse)
def get_movie_keywords(movie_id: int, db: Session = Depends(get_db)):
    """Get keywords for a movie"""
    query = "SELECT id, keywords FROM keywords WHERE movie_id = %s"
    result = db.execute(text(query), {"id": movie_id})
    keywords = result.fetchone()
    
    if not keywords:
        raise HTTPException(status_code=404, detail="Keywords not found")
    
    return keywords._mapping


@router.get("/{movie_id}/credits", response_model=CreditResponse)
def get_movie_credits(movie_id: int, db: Session = Depends(get_db)):
    """Get cast and crew for a movie"""
    query = "SELECT id, cast, crew FROM credits WHERE movie_id = %s"
    result = db.execute(text(query), {"id": movie_id})
    credits = result.fetchone()
    
    if not credits:
        raise HTTPException(status_code=404, detail="Credits not found")
    
    return credits._mapping
