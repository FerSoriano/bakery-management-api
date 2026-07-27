from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings 

engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
)

# The SessionMaker: A factory that provides async sessions for each request
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# The Base Class: All our models (Tables) will inherit from this
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session per request.
    Ensures the session is properly closed after the request finishes.
    """
    async with AsyncSessionLocal() as session:
        yield session
