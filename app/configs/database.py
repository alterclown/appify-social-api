"""
====================================================================================
  appify_social_api

  Date          : 7/11/2026 11:55 PM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# Switched from os.getenv to python-decouple
from decouple import config

# 1. Pull the database URL from your environment variables (.env)
DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql+asyncpg://postgres:password@localhost:5432/appify-social-db"
)

# 2. Initialize the Async Engine with optimization parameters
engine = create_async_engine(
    DATABASE_URL,
    echo=False,                # Set to True to see raw SQL logs in the terminal
    pool_size=20,              # Persistent open connections
    max_overflow=10,           # Extra connections allowed during peak traffic bursts
    pool_recycle=1800,         # Recycles connections every 30 minutes
    pool_pre_ping=True,        # Checks connection health before running queries
)

# 3. Create the session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,    # Prevents extra database hits after commits
)

# 4. FastAPI Dependency Provider
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an asynchronous database session per request.
    Closes the connection cleanly when the request lifecycle ends.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()