from shared.infrastructure.shared.sqlalchemy.config import postgres_db_settings
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

engine: AsyncEngine = create_async_engine(url=postgres_db_settings.get_db_url)

sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
