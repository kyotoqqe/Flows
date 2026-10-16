import time
import uuid
from dataclasses import asdict

from shared.application.exceptions import EntityAlreadyExist, EntityNotFound
from shared.application.handlers.handlers import CommandHandler
from src.auth.application.commands import (
    ActivateUser,
    BanUser,
    DeactivateUser,
    LoginUserWithPasword,
    LogOutUser,
    RefreshUserSession,
    RegisterOrLoginUserWithOauth,
    RegisterUser,
    UnbanUser,
    UnlinkOauthProvider,
)
from src.auth.application.dto import TokensPair, UserActivationTokenPayload
from src.auth.application.events import UserActivationRequested
from src.auth.application.exceptions import ActivationTimeExpired, PasswordsMismatchException
from src.auth.application.external.oauth import AbstractOauthClient
from src.auth.application.ports.tokens import AbstractAccessTokenProvider
from src.auth.application.ports.uow import SessionGroupsUoW, UsersUoW
from src.auth.domain.aggregate import User, SessionGroup
from src.auth.domain.exceptions import UserBanException
from src.auth.domain.services import UserBanningService
from src.auth.domain.value_objs import Email, PasswordHash, UserId
from src.auth.infrastructure.security.hasher import AbstractPasswordHasher
from src.auth.infrastructure.security.tokens import AbstractTokenGenerator


USER_TOKEN_ACTIVATION_LIFESPAN_MINUTES = 60 * 15


class RegisterUserHandler(CommandHandler[RegisterUser]):
    def __init__(
        self,
        uow: UsersUoW,
        password_hasher: AbstractPasswordHasher,
        token_generator: AbstractTokenGenerator,
    ) -> None:
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_generator = token_generator

    async def __call__(self, cmd: RegisterUser):
        async with self.uow:
            password = PasswordHash.validate_raw_password(cmd.password)
            user = await self.uow.users.get(email=Email.create(cmd.email))
            if user:
                raise EntityAlreadyExist(User, email=cmd.email)

            hashed_password = await self.password_hasher.async_hash_password(password)
            new_user = User.create(email_str=cmd.email, password_hash_str=hashed_password)

            user_activation_token = self.token_generator.encrypt(
                {
                    "user_id": str(new_user.aggregate_id),
                    "expires_at": time.time() + USER_TOKEN_ACTIVATION_LIFESPAN_MINUTES,
                }
            )
            self.uow.events.append(
                UserActivationRequested(
                    correlation_id=cmd.correlation_id,
                    event_id=uuid.uuid4(),
                    email=cmd.email,
                    activation_token=user_activation_token,
                )
            )
            new_user = await self.uow.users.add(new_user)
            await self.uow.commit()


class RegisterOrLoginUserWithOauthHandler(CommandHandler[RegisterOrLoginUserWithOauth]):
    def __init__(
        self,
        users_uow: UsersUoW,
        session_groups_uow: SessionGroupsUoW,
        oauth_client: AbstractOauthClient,
        access_token_provider: AbstractAccessTokenProvider,
    ) -> None:
        self.users_uow = users_uow
        self.session_groups_uow = session_groups_uow
        self.oauth_client = oauth_client
        self.access_token_provider = access_token_provider

    async def __call__(self, cmd: RegisterOrLoginUserWithOauth) -> TokensPair:
        user_creds = await self.oauth_client.get_user_credentials(code=cmd.code, state=cmd.state)

        async with self.users_uow:
            user = await self.users_uow.users.get(email=Email.create(user_creds.email))

            if user:
                if user.ban_info:
                    raise UserBanException("The user has an active ban")
                user.version_num += 1
            else:
                user = User.create(email_str=user_creds.email)
                user.is_active = True
                await self.users_uow.users.add(user)

            user.add_oauth_provider(
                provider_user_id=user_creds.provider_user_id, provider=user_creds.provider
            )
            await self.users_uow.users.update(user, aggregate_id=user.aggregate_id)
            await self.users_uow.commit()

        async with self.session_groups_uow:
            session_group = await self.session_groups_uow.session_groups.get(
                user_id=user.aggregate_id
            )

            if session_group is None:
                session_group = SessionGroup.create(user_id=user.aggregate_id)
                await self.session_groups_uow.session_groups.add(session_group)
            else:
                session_group.version_num += 1

            refresh_session = session_group.add_refresh_session(
                user_agent=cmd.user_agent, ip_addr=cmd.ip_addr
            )

            await self.session_groups_uow.session_groups.update(
                session_group, aggregate_id=session_group.aggregate_id
            )

            access_token = self.access_token_provider.encode(
                {
                    "user_id": str(user.aggregate_id),
                    "email": str(user.email),
                    "role": user.role,
                    "is_active": user.is_active,
                }
            )

            await self.session_groups_uow.commit()

            return TokensPair(
                access_token=access_token, refresh_token=str(refresh_session.refresh_token)
            )


class LoginUserWithPasswordHandler(CommandHandler[LoginUserWithPasword]):
    def __init__(
        self,
        users_uow: UsersUoW,
        session_groups_uow: SessionGroupsUoW,
        password_hasher: AbstractPasswordHasher,
        access_token_provider: AbstractAccessTokenProvider,
    ) -> None:
        self.users_uow = users_uow
        self.session_groups_uow = session_groups_uow
        self.password_hasher = password_hasher
        self.access_token_provider = access_token_provider

    async def __call__(self, cmd: LoginUserWithPasword) -> TokensPair:
        async with self.users_uow:
            user = await self.users_uow.users.get(email=Email.create(cmd.email))

            if not user:
                raise EntityNotFound(entity=User, email=cmd.email)

            if user.ban_info:
                raise UserBanException("The user has an active ban")

            if user.password_hash is None or not await self.password_hasher.async_verify_password(
                cmd.password, str(user.password_hash)
            ):
                raise PasswordsMismatchException("Passwords do not match")

        async with self.session_groups_uow:
            session_group = await self.session_groups_uow.session_groups.get(
                user_id=user.aggregate_id
            )
            if session_group is None:
                session_group = SessionGroup.create(user_id=user.aggregate_id)
                await self.session_groups_uow.session_groups.add(session_group)
            else:
                session_group.version_num += 1

            refresh_session = session_group.add_refresh_session(
                user_agent=cmd.user_agent, ip_addr=cmd.ip_addr
            )
            await self.session_groups_uow.session_groups.update(
                session_group, aggregate_id=session_group.aggregate_id
            )

            access_token = self.access_token_provider.encode(
                {
                    "user_id": str(user.aggregate_id),
                    "email": str(user.email),
                    "role": user.role,
                    "is_active": user.is_active,
                }
            )
            await self.session_groups_uow.commit()

            return TokensPair(
                access_token=access_token, refresh_token=str(refresh_session.refresh_token)
            )


class LogOutUserHandler(CommandHandler[LogOutUser]):
    def __init__(self, uow: SessionGroupsUoW) -> None:
        self.uow = uow

    async def __call__(self, cmd: LogOutUser):
        async with self.uow:
            session_group = await self.uow.session_groups.get(user_id=UserId(value=cmd.user_id))

            if session_group is None:
                raise EntityNotFound(entity=SessionGroup)

            session_group.remove_refresh_session(cmd.refresh_token)
            await self.uow.session_groups.update(session_group)
            await self.uow.commit()


class RefreshUserSessionHandler(CommandHandler[RefreshUserSession]):
    def __init__(
        self, uow: SessionGroupsUoW, access_token_provider: AbstractAccessTokenProvider
    ) -> None:
        self.uow = uow
        self.access_token_provider = access_token_provider

    async def __call__(self, cmd: RefreshUserSession) -> TokensPair:
        async with self.uow:
            session_group = await self.uow.session_groups.get(user_id=UserId(value=cmd.user_id))

            if not session_group:
                raise EntityNotFound(entity=SessionGroup)

            refresh_session = session_group.refresh_session(refresh_token=cmd.refresh_token)

            access_token = self.access_token_provider.encode(
                {
                    "user_id": str(cmd.user_id),
                    "email": str(cmd.email),
                    "role": cmd.role,
                    "is_active": cmd.is_active,
                }
            )

            await self.uow.session_groups.update(session_group)
            await self.uow.commit()

        return TokensPair(
            access_token=access_token, refresh_token=str(refresh_session.refresh_token)
        )


class ActivateUserHandler(CommandHandler[ActivateUser]):
    def __init__(self, uow: UsersUoW, token_generator: AbstractTokenGenerator) -> None:
        self.uow = uow
        self.token_generator = token_generator

    async def __call__(self, cmd: ActivateUser):
        payload = self.token_generator.decrypt(cmd.activation_token)

        if time.time() > payload["expires_at"]:
            raise ActivationTimeExpired

        async with self.uow:
            user = await self.uow.users.get(aggregate_id=UserId(uuid.UUID(payload["user_id"])))

            if user is None:
                raise EntityNotFound(entity=User)

            user.activate()
            await self.uow.users.update(user)
            await self.uow.commit()


class UnlinkOauthProviderHandler(CommandHandler[UnlinkOauthProvider]):
    def __init__(self, uow: UsersUoW) -> None:
        self.uow = uow

    async def __call__(self, cmd: UnlinkOauthProvider):
        async with self.uow:
            user = await self.uow.users.get(aggregate_id=UserId(value=cmd.user_id))

            if user is None:
                raise EntityNotFound(entity=User)

            user.unlink_oauth_provider(cmd.provider)
            user.version_num += 1
            await self.uow.commit()


class BanUserHandler(CommandHandler[BanUser]):
    def __init__(self, uow: UsersUoW) -> None:
        self.uow = uow

    async def __call__(self, cmd: BanUser):
        async with self.uow:
            user = await self.uow.users.get(aggregate_id=UserId(value=cmd.user_id))
            target = await self.uow.users.get(aggregate_id=UserId(value=cmd.target_user_id))

            if user is None or target is None:
                raise EntityNotFound(entity=User)

            if not UserBanningService().check_can_ban(user=user, target=target):
                raise UserBanException("You don't have permission to ban this user.")

            target.ban(
                banned_by=user.aggregate_id,
                expires_at=cmd.expires_at,
                reason=cmd.reason,
            )
            target.version_num += 1
            await self.uow.users.update(target)
            await self.uow.commit()


class UnbanUserHandler(CommandHandler[UnbanUser]):
    def __init__(self, uow: UsersUoW) -> None:
        self.uow = uow

    async def __call__(self, cmd: UnbanUser):
        async with self.uow:
            user = await self.uow.users.get(aggregate_id=UserId(value=cmd.user_id))
            target = await self.uow.users.get(aggregate_id=UserId(value=cmd.target_user_id))

            if user is None or target is None:
                raise EntityNotFound(entity=User)

            if not UserBanningService().check_can_ban(user=user, target=target):
                raise UserBanException("You don't have permission to ban this user.")

            target.unban()
            target.version_num += 1
            await self.uow.users.update(target)
            await self.uow.commit()


class DeactivateUserHandler(CommandHandler[DeactivateUser]):
    def __init__(self, uow: UsersUoW) -> None:
        self.uow = uow

    async def __call__(self, cmd: DeactivateUser):
        async with self.uow:
            user = await self.uow.users.get(aggregate_id=UserId(value=cmd.user_id))

            if user is None:
                raise EntityNotFound(entity=User, aggregate_id=str(cmd.user_id))

            user.deactivate()
            user.version_num += 1
            await self.uow.users.update(user)
            await self.uow.commit()


class DeleteRefreshSessionHandler(CommandHandler):
    pass


class DeleteAllRefreshSessionsHandler(CommandHandler):
    pass
