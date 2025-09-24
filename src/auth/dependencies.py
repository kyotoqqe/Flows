from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated

from src.auth.services import AuthService
from src.auth.units_of_work import SQLAlchemyUsersUnitOfWork
from src.auth.schemas import UserSchema

oauth2_scheme_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_user(token: Annotated[str, Depends(oauth2_scheme_bearer)]) -> UserSchema:
    service = AuthService(uow=SQLAlchemyUsersUnitOfWork())
    return await service.get_user(token)

async def get_active_user(user: Annotated[UserSchema, Depends(get_user)]) -> UserSchema:
    if not user.active:
        raise #UserDontActive

    return user