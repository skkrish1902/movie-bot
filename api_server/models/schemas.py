"""
Pydantic models for API responses
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MovieBase(BaseModel):
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None


class MovieResponse(MovieBase):
    id: int
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[float] = None
    popularity: Optional[float] = None
    genres: Optional[List[Dict[str, Any]]] = None
    poster_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class RatingResponse(BaseModel):
    user_id: int
    movie_id: int
    rating: float
    timestamp: int


class KeywordResponse(BaseModel):
    id: int
    keywords: Optional[List[Dict[str, Any]]] = None


class CreditResponse(BaseModel):
    id: int
    cast: Optional[List[Dict[str, Any]]] = None
    crew: Optional[List[Dict[str, Any]]] = None


class MovieDetailResponse(MovieResponse):
    credits: Optional[CreditResponse] = None
    keywords: Optional[KeywordResponse] = None
    ratings: Optional[List[RatingResponse]] = None


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


class SearchResponse(BaseModel):
    results: List[MovieResponse]
    total_count: int


class RecommendationRequest(BaseModel):
    movie_id: int
    limit: Optional[int] = 5


class RecommendationResponse(BaseModel):
    movie_id: int
    recommendations: List[MovieResponse]
