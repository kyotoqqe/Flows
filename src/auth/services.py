import uuid

from src.core.domain.exceptions import EntityNotFound, EntityAlreadyExist
from src.core.interfaces.tasks_queue import AbstractTaskQueue

from src.auth.interfaces.units_of_work import UsersUnitOfWork, RefreshSessionsUnitOfwork
from src.auth.domain.entities import User
from src.auth.domain.value_obj import RefreshSession, UserRole
from src.auth.domain.services import ProfileCreator
from src.auth.infrastructure.dto import Base64TokenPayload, JWTTokenPayload, Token, PasswordResetTokenPayload
from src.auth.domain.services import CheckRefreshSessionCount

from src.auth.infrastructure.utils import generated_password_hash, create_confirmation_link, \
                                          generate_token, decode_token, \
                                          verify_password, create_password_reset_link
from src.auth.infrastructure.jwt.config import jwt_settings
from src.auth.infrastructure.jwt.utils import create_jwt_token, decode_jwt_token
from src.auth.infrastructure.exceptions import PasswordDontMatchException

from src.mailing.interface import AbstractEmailSender

from src.profiles.interfaces.units_of_work import ProfilesUnitOfWork


from datetime import datetime, timezone, timedelta
from typing import Optional


class AuthService:

    def __init__(self, 
                 uow: Optional[UsersUnitOfWork] = None, 
                 redis_uow: Optional[RefreshSessionsUnitOfwork] = None):
        self._uow = uow
        self._redis_uow = redis_uow
    
    async def get_user(self, jwt_token: str):
        async with self._uow:
            user_data = decode_jwt_token(jwt_token)
            user = await self._uow.users.get(id=user_data.user_id)

            if not user:
                raise EntityNotFound(
                    User, 
                    user_id=user.id
                )

            return user
    
    async def check_credentials(self):
        pass
    
    async def registration(self, 
                        email: str,
                        username: str,
                        password:str,
                        task_queue:AbstractTaskQueue,
                        email_sender: AbstractEmailSender
            ):
        async with self._uow:
            user = await self._uow.users.get(email=email)

            if user:
                raise EntityAlreadyExist(
                    User,
                    email=email
                )

            password_hash = generated_password_hash(password)

            user = User(
                email=email,
                password=password_hash,
                role=UserRole.member
            )
            
            user = await self._uow.users.add(
                user, 
                exclude={"id", "created_at", "updated_at"}
            )

            await self._uow.commit()

            payload = Base64TokenPayload(
                user_id=user.id,
                username=username
            )
            token = generate_token(payload)
            task_queue.execute(
                email_sender.send_email,
                username,
                user.email,
                create_confirmation_link(token), 
            )
            return user
    
    async def confirm_user(self,profiles_uow: ProfilesUnitOfWork, token: str):
        user_payload = decode_token(token)
        async with self._uow:
            user = await self._uow.users.get(id=user_payload.user_id)

            if not user:
                raise EntityNotFound
            
            user.active = True
            user = await self._uow.users.update(user, id=user.id)
            #call profile service
            #use event driven
            await ProfileCreator.create(uow=profiles_uow, user_id=user.id, username=user_payload.username)
            await self._uow.commit()
            return user

    async def login(self, email: str, password: str) -> Token:
        async with self._uow:
            user = await self._uow.users.get(email=email)

            if not user:
                raise EntityNotFound(
                    model=User,
                    email=email,
                )
            
            if not verify_password(
                        input_password=password, 
                        password_hash=user.password
                    ):
                raise PasswordDontMatchException 
            
            user_payload = JWTTokenPayload(
                user_id= user.id,
                exp= datetime.now(timezone.utc) + timedelta(minutes=jwt_settings.access_token_expire_minutes),
                role=user.role
            )

            access_token = create_jwt_token(payload=user_payload)
            
            async with self._redis_uow:
                user_sessions = await self._redis_uow.refresh_sessions.get(user_id=user.id)

                CheckRefreshSessionCount().check_rule(len(user_sessions))
            
                refresh_session = RefreshSession(
                    user_id=user.id,
                    token=str(uuid.uuid4()),
                    expires_in= 60 * 60 * 24 * jwt_settings.refresh_token_expire_days
                )

                await self._redis_uow.refresh_sessions.add(
                    refresh_session,
                    exclude = {"created_at"},
                    ttl=60 * 60 * 24 * jwt_settings.refresh_token_expire_days 
                )
                await self._redis_uow.commit()

            await self._uow.commit()
            return Token(
                access=access_token,
                refresh=refresh_session.token
            )
        
    async def logout(self, user_id: int, refresh_token: str):
        async with self._redis_uow:
            refresh_session = await self._redis_uow.refresh_sessions.get(token=refresh_token)

            if not refresh_session:
                raise EntityNotFound(
                    model=RefreshSession,
                    token=refresh_token
                )

            await self._redis_uow.refresh_sessions.delete(user_id=user_id, token=refresh_token)
            await self._redis_uow.commit()
    
    async def refresh(self, user_id: int, refresh_token: str) -> Token:
        async with self._redis_uow:
            refresh_session = await self._redis_uow.refresh_sessions.get(scalar=True, token=refresh_token)

            if not refresh_session:
                raise EntityNotFound(
                    model=RefreshSession,
                    token=refresh_token
                )
            
            user = await self._uow.users.get(id=user_id)

            if not user:
                raise EntityNotFound(
                    model=User,
                    id=user_id
                )

            user_payload = JWTTokenPayload(
                user_id = refresh_session.user_id,
                role = user.role,
                exp = (datetime.now(timezone.utc) + timedelta(minutes=jwt_settings.access_token_expire_minutes)).isoformat()
            )

            access_token = create_jwt_token(user_payload)
            new_refresh_session = RefreshSession(
                user_id= refresh_session.user_id,
                token=str(uuid.uuid4()),
                expires_in= 60 * 60 * 24 * jwt_settings.refresh_token_expire_days
            )

            await self._redis_uow.refresh_sessions.delete(user_id=user_id, token=refresh_token)
            await self._redis_uow.refresh_sessions.add(
                new_refresh_session, 
                exclude = {"created_at"},
                ttl=60 * 60 * 24 * jwt_settings.refresh_token_expire_days
            )

            await self._redis_uow.commit()

            return Token(
                access=access_token,
                refresh=new_refresh_session.token
            )

    async def password_reset(self, 
            email: str,
            task_queue: AbstractTaskQueue,
            email_sender: AbstractEmailSender,
            profiles_uow: ProfilesUnitOfWork
        ):
        async with self._uow:
            user = await self._uow.users.get(email=email)

            if not user:
                raise EntityNotFound(
                    model=User,
                    email=email
                )

            async with profiles_uow:
                profile = await profiles_uow.profiles.get(user_id=user.id)

            payload = PasswordResetTokenPayload(
                user_id=user.id
            )
            token = generate_token(payload)

            task_queue.execute(
                email_sender.send_email,
                profile.username,
                user.email,
                create_password_reset_link(token)
            )
    
    async def password_reset_confirm(self, token: str, password: str):
        pass