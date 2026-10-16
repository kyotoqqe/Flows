import datetime
from ipaddress import IPv4Address
import time
from uuid import UUID

import pytest

from shared.application.handlers.registry import HandlerRegistry
from shared.application.messagebus import MessageBus
from src.auth.application.commands import (
    ActivateUser,
    LogOutUser,
    LoginUserWithPasword,
    RefreshUserSession,
    RegisterOrLoginUserWithOauth,
    RegisterUser,
    UnlinkOauthProvider,
)
from src.auth.application.dto import TokensPair
from src.auth.application.exceptions import PasswordsMismatchException
from src.auth.application.handlers import (
    ActivateUserHandler,
    LogOutUserHandler,
    LoginUserWithPasswordHandler,
    RefreshUserSessionHandler,
    RegisterOrLoginUserWithOauthHandler,
    RegisterUserHandler,
    UnlinkOauthProviderHandler,
)
from src.auth.domain.aggregate import SessionGroup, User
from src.auth.domain.exceptions import UserBanException
from src.auth.domain.value_objs import Email, PasswordHash, Provider, UserId
from tests.auth.fakes.access_tokens import FakeAccessTokenProvider
from tests.auth.fakes.hasher import FakePasswordHasher
from tests.auth.fakes.oauth import FakeOauthClient, FakeStateManager
from tests.auth.fakes.repository import FakeSessionGroupsRepository, FakeUsersRepository
from tests.auth.fakes.tokens import FakeTokenGenerator
from tests.auth.fakes.uow import FakeSessionGroupsUoW, FakeUsersUoW
from tests.auth.unit.domain.test_user import get_user

test_registry = HandlerRegistry()
mbs = MessageBus()
mbs.registry = test_registry


@pytest.mark.asyncio
async def test_register_user():
    uow = FakeUsersUoW()
    hasher = FakePasswordHasher()
    token_generator = FakeTokenGenerator()

    test_registry.register(
        RegisterUserHandler(uow=uow, password_hasher=hasher, token_generator=token_generator),
        RegisterUser,
    )

    cmd = RegisterUser(email="anton200705@gmail.com", password="hDM\172S!]9£")
    await mbs.handle(cmd)

    assert isinstance(await uow.users.get(email=Email(value="anton200705@gmail.com")), User)
    assert len(uow.outbox) == 2


@pytest.mark.asyncio
async def test_user_register_or_login_with_oauth():
    users_uow = FakeUsersUoW()
    session_groups_uow = FakeSessionGroupsUoW()
    state_manager = FakeStateManager()
    oauth_client = FakeOauthClient(state_manager)
    access_token_provider = FakeAccessTokenProvider()

    test_registry.register(
        RegisterOrLoginUserWithOauthHandler(
            users_uow=users_uow,
            session_groups_uow=session_groups_uow,
            oauth_client=oauth_client,
            access_token_provider=access_token_provider,
        ),
        RegisterOrLoginUserWithOauth,
    )

    state = await state_manager.set_state()
    cmd = RegisterOrLoginUserWithOauth(
        code="e65a5d1d-640f-479f-a7d3-68b1ca8d8793",
        state=state,
        user_agent="Back-end 1.1",
        ip_addr=IPv4Address("192.168.1.1"),
    )

    await mbs.handle(cmd)
    print(mbs.command_result)
    assert isinstance(mbs.command_result, TokensPair)
    user = await users_uow.users.get(email=Email(value="test.email@gmail.com"))
    assert isinstance(user, User)
    assert len(user.oauth_providers) == 1
    assert len(users_uow.outbox) == 1

    session_group = await session_groups_uow.session_groups.get(user_id=user.aggregate_id)
    assert isinstance(session_group, SessionGroup)
    assert len(session_group) == 1

    user.ban(
        banned_by=UserId(UUID("6d191428-4968-4579-852d-99a257b8d86a")),
        expires_at=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=7),
        reason="chmo",
    )

    try:
        await mbs.handle(cmd)
    except UserBanException:
        assert True
        return

    assert False


@pytest.mark.asyncio
async def test_login_user_with_password():
    users_uow = FakeUsersUoW()
    session_groups_uow = FakeSessionGroupsUoW()
    hasher = FakePasswordHasher()
    access_token_provider = FakeAccessTokenProvider()

    test_registry.register(
        LoginUserWithPasswordHandler(
            users_uow=users_uow,
            session_groups_uow=session_groups_uow,
            password_hasher=hasher,
            access_token_provider=access_token_provider,
        ),
        LoginUserWithPasword,
    )
    cmd = LoginUserWithPasword(
        email="anton200705@gmail.com",
        password="hDM\172S!]9£",
        user_agent="Back-end 1.1",
        ip_addr=IPv4Address("192.168.1.1"),
    )

    u_repo = FakeUsersRepository()
    sg_repo = FakeSessionGroupsRepository()
    user = await u_repo.get(email=Email.create(cmd.email))
    if not user:
        assert False
    # await sg_repo.add(SessionGroup.create(user_id=user.aggregate_id))
    await mbs.handle(cmd)
    assert isinstance(mbs.command_result, TokensPair)

    session_group = await session_groups_uow.session_groups.get(user_id=user.aggregate_id)
    assert isinstance(session_group, SessionGroup)
    assert len(session_group) == 1

    try:
        cmd = LoginUserWithPasword(
            email="anton200705@gmail.com",
            password="some_password",
            user_agent="Back-end 1.1",
            ip_addr=IPv4Address("192.168.1.1"),
        )

        await mbs.handle(cmd)
    except Exception as e:
        assert isinstance(e, PasswordsMismatchException)

    user.password_hash = None

    try:
        cmd = LoginUserWithPasword(
            email="anton200705@gmail.com",
            password="some_password",
            user_agent="Back-end 1.1",
            ip_addr=IPv4Address("192.168.1.1"),
        )

        await mbs.handle(cmd)
    except Exception as e:
        assert isinstance(e, PasswordsMismatchException)
        return

    assert False


@pytest.mark.asyncio
async def test_logout_user_handler():
    uow = FakeSessionGroupsUoW()
    test_registry.register(LogOutUserHandler(uow=uow), LogOutUser)

    u_r = FakeUsersRepository()
    user = await u_r.get(email=Email.create("anton200705@gmail.com"))
    if not user:
        assert False
    async with uow:
        sg = await uow.session_groups.get(user_id=user.aggregate_id)
        if sg is not None:
            rs_count = len(sg.refresh_sessions)
            if len(sg.refresh_sessions) > 0:
                refresh_token = sg.refresh_sessions[0].refresh_token
            else:
                assert False
        else:
            assert False

    cmd = LogOutUser(user_id=user.aggregate_id.value, refresh_token=refresh_token)
    await mbs.handle(cmd)

    assert len(sg.refresh_sessions) == rs_count - 1


@pytest.mark.asyncio
async def test_refresh_user_session():
    uow = FakeSessionGroupsUoW()
    access_token_provider = FakeAccessTokenProvider()

    test_registry.register(
        RefreshUserSessionHandler(uow=uow, access_token_provider=access_token_provider),
        RefreshUserSession,
    )

    u_r = FakeUsersRepository()
    user = await u_r.get(email=Email.create("anton200705@gmail.com"))
    if not user:
        assert False
    async with uow:
        sg = await uow.session_groups.get(user_id=user.aggregate_id)
        if sg is not None:
            sg.add_refresh_session(user_agent="Back-end 1.1", ip_addr=IPv4Address("192.168.1.1"))
            await uow.session_groups.update(sg)
            rs_count = len(sg.refresh_sessions)
            if len(sg.refresh_sessions) > 0:
                refresh_token = sg.refresh_sessions[0].refresh_token
            else:
                assert False

        else:
            assert False

    cmd = RefreshUserSession(
        user_id=user.aggregate_id.value,
        email=str(user.email),
        role=user.role,
        is_active=user.is_active,
        refresh_token=refresh_token,
        user_agent="Back-end 1.1",
        ip_addr=IPv4Address("192.168.1.1"),
    )

    await mbs.handle(cmd)
    assert isinstance(mbs.command_result, TokensPair)


@pytest.mark.asyncio
async def test_activate_user():
    USER_TOKEN_ACTIVATION_LIFESPAN_MINUTES = 60 * 15
    uow = FakeUsersUoW()
    token_generator = FakeTokenGenerator()

    u_r = FakeUsersRepository()
    user = await u_r.get(email=Email.create("anton200705@gmail.com"))
    if not user:
        assert False

    payload = {
        "user_id": str(user.aggregate_id),
        "expires_at": time.time() + USER_TOKEN_ACTIVATION_LIFESPAN_MINUTES,
    }
    token = token_generator.encrypt(payload)

    assert isinstance(token, str)

    test_registry.register(
        ActivateUserHandler(uow=uow, token_generator=token_generator), ActivateUser
    )

    cmd = ActivateUser(activation_token=token)

    await mbs.handle(cmd)

    assert user.is_active


@pytest.mark.asyncio
async def test_unlink_oauth_provider():
    uow = FakeUsersUoW()

    test_registry.register(UnlinkOauthProviderHandler(uow=uow), UnlinkOauthProvider)

    u_r = FakeUsersRepository()
    user = await u_r.get(email=Email.create("anton200705@gmail.com"))
    if not user:
        assert False

    user.password_hash = PasswordHash(value="some_password")

    user.add_oauth_provider(
        provider=Provider.SPOTIFY,
        provider_user_id="d8e11d09-72b7-448d-a495-e20567e203c0",
    )

    assert len(user.oauth_providers) == 1

    cmd = UnlinkOauthProvider(user_id=user.aggregate_id.value, provider=Provider.SPOTIFY)

    await mbs.handle(cmd)

    assert len(user.oauth_providers) == 0
