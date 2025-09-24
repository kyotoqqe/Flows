from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqlalchemy.orm import clear_mappers

from src.core.database.orm import start_mappers as images_mappers
from src.auth.infrastructure.database.orm import start_mappers as users_mappers
from src.profiles.infrastructure.database.orm import start_mappers as profiles_mappers

from src.auth.routers import router as auth_router
from src.profiles.routers import router as profiles_router

from src.core.redis.connection import redis_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    users_mappers()
    profiles_mappers()
    images_mappers()
    yield
    clear_mappers()
    await redis_connection.aclose()


app = FastAPI(
    lifespan=lifespan,
    root_path="/api"
)

app.include_router(auth_router)
app.include_router(profiles_router)