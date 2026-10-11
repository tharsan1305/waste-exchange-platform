import os
from typing import Generator, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from supabase import create_client, Client
from app.core.config import settings

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL if hasattr(settings, "DATABASE_URL") else "postgresql://postgres:postgres@localhost:5432/postgres"

# Create SQLAlchemy engine with pool_pre_ping to automatically recover from dropped connections
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()

def get_db() -> Generator:
    """
    FastAPI dependency that yields a SQLAlchemy database session
    and ensures it is properly closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Supabase Client Singleton
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Returns the singleton Supabase client using SUPABASE_URL and SUPABASE_ANON_KEY.
    """
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL") or settings.SUPABASE_URL
        key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or settings.SUPABASE_SERVICE_ROLE_KEY
        _supabase_client = create_client(url, key)
    return _supabase_client
