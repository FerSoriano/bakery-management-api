
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Environment variable DATABASE_URL is not set.")

# echo=True will print the generated SQL in the terminal (debugging)
engine = create_async_engine(DATABASE_URL, echo=True)

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