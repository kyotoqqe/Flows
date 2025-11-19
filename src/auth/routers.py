import aiohttp
import base64
import jwt

from fastapi import APIRouter, Response, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from pydantic import Base64Str, EmailStr

from typing import Annotated

from src.core.worker.tasks_queue import CeleryTaskQueue 
#maybe move app to __init__.py
from src.core.worker.celery import app

from src.auth.schemas import RegistrationSchema, UserSchema, PasswordResetSchema
from src.auth.units_of_work import SQLAlchemyUsersUnitOfWork, RedisRefreshSessionsUnitOfWork
from src.auth.services import AuthService
from src.auth.config import cookie_settings
from src.auth.infrastructure.utils import oauth2_scheme_cookie
from src.auth.dependencies import get_active_user
from src.auth.infrastructure.oauth2 import generate_spotify_oauth_redirect_uri, generate_google_oauth_redirect_url

from src.mailing.service import SMTPConfirmationEmailSender, SMTPPasswordResetEmailSender

from src.profiles.units_of_work import SQLAlchemyProfilesUnitOfWork

router = APIRouter(
    prefix="/auth",
    tags=["Authentification & Authorization"]
)

@router.post("/registration")
async def registraion(user_data: RegistrationSchema) -> UserSchema:
    user_data = user_data.model_dump(exclude={"password2"})
    service = AuthService(uow=SQLAlchemyUsersUnitOfWork())
    return await service.registration(
        task_queue=CeleryTaskQueue(app=app),
        email_sender=SMTPConfirmationEmailSender(),
        **user_data
    )
    

@router.get("/confirm")
async def registration_confirm(token:str) -> UserSchema:
    service = AuthService(uow=SQLAlchemyUsersUnitOfWork())
    return await service.confirm_user(
        profiles_uow=SQLAlchemyProfilesUnitOfWork(),
        token=token
    )

@router.post("/login")
async def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
        response: Response
    ) :
    user_data = {
        "email": user_data.username,
        "password": user_data.password
    }
    service = AuthService(
        uow=SQLAlchemyUsersUnitOfWork(),
        redis_uow=RedisRefreshSessionsUnitOfWork()
    )
    tokens =  await service.login(**user_data)

    response.set_cookie(
        key=cookie_settings.cookie_key,
        value=tokens.refresh,
        max_age=cookie_settings.max_age,
        path=cookie_settings.cookie_path,
        domain=cookie_settings.cookie_domain,
        secure=cookie_settings.cookie_secure,
        samesite=cookie_settings.cookie_samesite,
        httponly=cookie_settings.cookie_httponly
    )

    return {"access_token":tokens.access, "token_type": "bearer"}

@router.post("/logout")
async def logout(
    user: Annotated[UserSchema, Depends(get_active_user)],
    response: Response, 
    refresh_token: Annotated[str, Depends(oauth2_scheme_cookie)]
):
    service = AuthService(
        uow=SQLAlchemyUsersUnitOfWork(),
        redis_uow=RedisRefreshSessionsUnitOfWork()
    )
    await service.logout(user_id=user.id, refresh_token=refresh_token)

    response.delete_cookie(
        key=cookie_settings.cookie_key,
        path=cookie_settings.cookie_path,
        domain=cookie_settings.cookie_domain,
        secure=cookie_settings.cookie_secure,
        samesite=cookie_settings.cookie_samesite,
        httponly=cookie_settings.cookie_httponly
    )

    return {"message":"LogOut successful"}

#fix that
@router.post("/token/refresh")
async def refresh(
    user: Annotated[UserSchema, Depends(get_active_user)],
    response: Response, 
    refresh_token: Annotated[str, Depends(oauth2_scheme_cookie)]
) -> str:
    service = AuthService(
        uow=SQLAlchemyUsersUnitOfWork(),
        redis_uow=RedisRefreshSessionsUnitOfWork()
    )
    tokens =  await service.refresh(user_id=user.id, refresh_token=refresh_token)

    response.set_cookie(
        key=cookie_settings.cookie_key,
        value=tokens.refresh,
        max_age=cookie_settings.max_age,
        path=cookie_settings.cookie_path,
        domain=cookie_settings.cookie_domain,
        secure=cookie_settings.cookie_secure,
        samesite=cookie_settings.cookie_samesite,
        httponly=cookie_settings.cookie_httponly
    )

    return tokens.access

@router.get("/users/me")
async def get_me(user: Annotated[UserSchema, Depends(get_active_user)]) -> UserSchema:
    return user

@router.post("/password/reset/request")
async def password_reset(email: EmailStr):
    service = AuthService(uow=SQLAlchemyUsersUnitOfWork())
    await service.password_reset(
        email=email,
        task_queue=CeleryTaskQueue(app=app),
        email_sender=SMTPPasswordResetEmailSender(),
        profiles_uow=SQLAlchemyProfilesUnitOfWork(),
    )
    

@router.post("/password/reset/confirm")
async def reset_confirm(reset_data:PasswordResetSchema):
    service = AuthService(
        uow=SQLAlchemyUsersUnitOfWork()
    )
    reset_dict = reset_data.model_dump(exclude={"password2"})
    await service.password_reset_confirm(**reset_dict)

