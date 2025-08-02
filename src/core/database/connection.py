from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from src.core.database.config import db_settings

from typing import AsyncGenerator

engine: AsyncEngine = create_async_engine(
    url=db_settings.get_db_url
)

session_maker: async_sessionmaker = async_sessionmaker(expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session