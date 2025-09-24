from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from src.core.database.config import db_settings


engine: AsyncEngine = create_async_engine(
    url=db_settings.get_db_url
)

session_maker: async_sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
