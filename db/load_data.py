"""
Database setup script to load movie datasets into PostgreSQL
"""
import os
import json
import pandas as pd
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "movie_bot")

# CSV file paths
DATASETS_DIR = os.path.join(os.path.dirname(__file__), "../datasets")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def create_database():
    """Create database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if not cursor.fetchone():
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_NAME)
            ))
            logger.info(f"Database '{DB_NAME}' created successfully")
        else:
            logger.info(f"Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


def create_tables(engine):
    """Create all necessary tables"""
    with engine.connect() as connection:
        # Movies table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                id BIGINT PRIMARY KEY,
                adult BOOLEAN,
                budget BIGINT,
                genres JSONB,
                homepage VARCHAR(500),
                imdb_id VARCHAR(20),
                original_language VARCHAR(10),
                original_title VARCHAR(500),
                overview TEXT,
                popularity FLOAT,
                poster_path VARCHAR(500),
                production_companies JSONB,
                production_countries JSONB,
                release_date DATE,
                revenue BIGINT,
                runtime FLOAT,
                spoken_languages JSONB,
                status VARCHAR(50),
                tagline TEXT,
                title VARCHAR(500),
                video BOOLEAN,
                vote_average FLOAT,
                vote_count INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Credits table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS credits (
                id BIGINT PRIMARY KEY,
                cast JSONB,
                crew JSONB,
                movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Keywords table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS keywords (
                id BIGINT PRIMARY KEY,
                movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
                keywords JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Ratings table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS ratings (
                id SERIAL PRIMARY KEY,
                user_id INT,
                movie_id INT,
                rating FLOAT,
                timestamp BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Links table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS links (
                movie_id INT PRIMARY KEY,
                imdb_id VARCHAR(20),
                tmdb_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        connection.commit()
        logger.info("Tables created successfully")


def load_movies(engine):
    """Load movies metadata"""
    try:
        csv_file = os.path.join(DATASETS_DIR, "movies_metadata.csv")
        logger.info(f"Loading movies from {csv_file}")
        
        df = pd.read_csv(csv_file, low_memory=False)
        
        # Convert data types
        df['adult'] = df['adult'].astype(bool)
        df['budget'] = pd.to_numeric(df['budget'], errors='coerce').astype('Int64')
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').astype('Int64')
        df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
        df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
        df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce').astype('Int64')
        
        # Keep JSON fields as strings for JSONB insertion
        json_columns = ['genres', 'production_companies', 'production_countries', 'spoken_languages', 'belongs_to_collection']
        for col in json_columns:
            if col in df.columns:
                df[col] = df[col].fillna('[]')
        
        # Select columns to insert
        columns_to_insert = [
            'id', 'adult', 'budget', 'genres', 'homepage', 'imdb_id',
            'original_language', 'original_title', 'overview', 'popularity',
            'poster_path', 'production_companies', 'production_countries',
            'release_date', 'revenue', 'runtime', 'spoken_languages',
            'status', 'tagline', 'title', 'video', 'vote_average', 'vote_count'
        ]
        
        df_insert = df[columns_to_insert].copy()
        df_insert = df_insert.drop_duplicates(subset=['id'])
        df_insert = df_insert[df_insert['id'].notna()]
        
        df_insert.to_sql('movies', engine, if_exists='append', index=False)
        logger.info(f"Loaded {len(df_insert)} movies")
    except Exception as e:
        logger.error(f"Error loading movies: {e}")
        raise


def load_credits(engine):
    """Load credits data"""
    try:
        csv_file = os.path.join(DATASETS_DIR, "credits.csv")
        logger.info(f"Loading credits from {csv_file}")
        
        df = pd.read_csv(csv_file)
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        df['movie_id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['id'])
        df = df[df['id'].notna()]
        
        df.to_sql('credits', engine, if_exists='append', index=False)
        logger.info(f"Loaded {len(df)} credit records")
    except Exception as e:
        logger.error(f"Error loading credits: {e}")
        raise


def load_keywords(engine):
    """Load keywords data"""
    try:
        csv_file = os.path.join(DATASETS_DIR, "keywords.csv")
        logger.info(f"Loading keywords from {csv_file}")
        
        df = pd.read_csv(csv_file)
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        df['movie_id'] = df['id']
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['id'])
        df = df[df['id'].notna()]
        
        df.to_sql('keywords', engine, if_exists='append', index=False)
        logger.info(f"Loaded {len(df)} keyword records")
    except Exception as e:
        logger.error(f"Error loading keywords: {e}")
        raise


def load_ratings(engine):
    """Load ratings data"""
    try:
        csv_file = os.path.join(DATASETS_DIR, "ratings.csv")
        logger.info(f"Loading ratings from {csv_file}")
        
        # Load in chunks to handle large file
        chunks = pd.read_csv(csv_file, chunksize=50000)
        for i, chunk in enumerate(chunks):
            chunk.columns = ['user_id', 'movie_id', 'rating', 'timestamp']
            chunk.to_sql('ratings', engine, if_exists='append', index=False)
            logger.info(f"Loaded ratings chunk {i+1}")
    except Exception as e:
        logger.error(f"Error loading ratings: {e}")
        raise


def load_links(engine):
    """Load links data"""
    try:
        csv_file = os.path.join(DATASETS_DIR, "links.csv")
        logger.info(f"Loading links from {csv_file}")
        
        df = pd.read_csv(csv_file)
        df.columns = ['movie_id', 'imdb_id', 'tmdb_id']
        df['tmdb_id'] = pd.to_numeric(df['tmdb_id'], errors='coerce').astype('Int64')
        
        df.to_sql('links', engine, if_exists='append', index=False)
        logger.info(f"Loaded {len(df)} link records")
    except Exception as e:
        logger.error(f"Error loading links: {e}")
        raise


def create_indexes(engine):
    """Create indexes for better query performance"""
    with engine.connect() as connection:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title)",
            "CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_ratings_movie_id ON ratings(movie_id)",
            "CREATE INDEX IF NOT EXISTS idx_links_imdb_id ON links(imdb_id)",
            "CREATE INDEX IF NOT EXISTS idx_keywords_movie_id ON keywords(movie_id)",
            "CREATE INDEX IF NOT EXISTS idx_credits_movie_id ON credits(movie_id)"
        ]
        
        for index in indexes:
            connection.execute(text(index))
        
        connection.commit()
        logger.info("Indexes created successfully")


def main():
    """Main function to run the data loading pipeline"""
    logger.info("Starting database setup...")
    
    # Create database
    create_database()
    
    # Connect to database
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    create_tables(engine)
    
    # Load data
    try:
        load_movies(engine)
        load_credits(engine)
        load_keywords(engine)
        load_links(engine)
        load_ratings(engine)
        create_indexes(engine)
        logger.info("Data loading completed successfully!")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
