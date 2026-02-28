from typing import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

# Fallback to async sqlite if a standard database_url without explicitly specifying sqlite is passed 
# while in reality it's local. Since settings config sets it by default it is robust.
# e.g., postgresql+asyncpg://user:password@localhost/dbname
engine = create_async_engine(
    settings.get_database_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.get_database_url else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency returning an asynchronous database session.
    Automatically closes session after endpoint executes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
