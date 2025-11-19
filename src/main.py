from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqlalchemy.orm import clear_mappers

from src.core.database.orm import start_mappers as images_mappers
from src.auth.infrastructure.database.orm import start_mappers as users_mappers
from src.profiles.infrastructure.database.orm import start_mappers as profiles_mappers
from src.organizations.organizations.infrastructure.database.orm import start_mappers as organizations_mappers

from src.auth.routers import router as auth_router
from src.profiles.routers import router as profiles_router
from src.organizations.organizations.api.router import router as organizations_router
from src.payments.api.router import router as payments_router

from src.core.redis.connection import redis_connection

from src.admin.middlewares import RefreshTokenMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    users_mappers()
    profiles_mappers()
    images_mappers()
    organizations_mappers()

    from src.admin.config import admin
    from src.admin.views import UserAdmin
    
    admin.add_view(UserAdmin)
    yield
    clear_mappers()
    await redis_connection.aclose()


app = FastAPI(
    lifespan=lifespan,
    root_path="/api"
)
#app.add_middleware(RefreshTokenMiddleware)
app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(organizations_router)
app.include_router(payments_router)