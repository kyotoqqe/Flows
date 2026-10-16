import datetime

from src.auth.domain.aggregate import User
from src.auth.domain.exceptions import OauthProviderException
from src.auth.domain.services import UserBanningService
from src.auth.domain.value_objs import PasswordHash, Provider, UserRole


def get_user():
    email_str = "anton200705@gmail.com"
    password = PasswordHash.validate_raw_password("hDM\172S!]9£")
    password_hash_str = str(hash(password))
    return User.create(email_str, password_hash_str)


def test_user_creation():
    email_str = "anton200705@gmail.com"
    password = PasswordHash.validate_raw_password("hDM\172S!]9£")
    password_hash_str = str(hash(password))
    user = User.create(email_str, password_hash_str)

    assert str(user.email) == email_str
    assert len(user.events) == 1


def test_unlink_oauth_provider():
    user = get_user()

    user.add_oauth_provider(
        provider=Provider.SPOTIFY,
        provider_user_id="d8e11d09-72b7-448d-a495-e20567e203c0",
    )
    user.add_oauth_provider(
        provider=Provider.GOOGLE, provider_user_id="b9684126-902d-478e-afe9-3d86f274c835"
    )

    assert len(user.oauth_providers) == 2

    user.unlink_oauth_provider(provider=Provider.SPOTIFY)
    user.unlink_oauth_provider(provider=Provider.GOOGLE)

    assert len(user.oauth_providers) == 0

    user.add_oauth_provider(
        provider=Provider.GOOGLE, provider_user_id="b9684126-902d-478e-afe9-3d86f274c835"
    )

    try:
        user.password_hash = None
        user.unlink_oauth_provider(provider=Provider.GOOGLE)
    except Exception as e:
        assert isinstance(e, OauthProviderException)


def test_user_ban():
    user = get_user()
    target = get_user()

    bans_service = UserBanningService()
    assert bans_service.check_can_ban(user, target) is False

    user.role = UserRole.ADMIN
    assert bans_service.check_can_ban(user, target) is True

    target.role = UserRole.ADMIN
    assert bans_service.check_can_ban(user, target) is False

    user.role = UserRole.OWNER
    assert bans_service.check_can_ban(user, target) is True

    target.role = UserRole.ADMIN
    assert bans_service.check_can_ban(user, target) is True

    target = user
    assert bans_service.check_can_ban(user, target) is False

    target = get_user()

    if bans_service.check_can_ban(user, target):
        target.ban(
            banned_by=user.aggregate_id,
            expires_at=datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=7),
            reason="chmo",
        )

    assert target.ban_info is not None
