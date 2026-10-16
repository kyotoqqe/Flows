from ipaddress import IPv4Address
import time

from src.auth.domain.aggregate import SessionGroup
from src.auth.domain.exceptions import RefreshSessionIsExpired, RefreshSessionLimitExceeded
from src.auth.domain.entities import RefreshSession
from tests.auth.unit.domain.test_user import get_user


def test_session_group():
    user = get_user()

    session_group = SessionGroup.create(user.aggregate_id)

    assert isinstance(session_group, SessionGroup)

    try:
        for _ in range(6):
            session_group.add_refresh_session(
                user_agent="Back-end 1.1", ip_addr=IPv4Address("192.168.1.1")
            )
    except Exception as e:
        assert isinstance(e, RefreshSessionLimitExceeded)
        session_group.delete_all_refreesh_sessions()

    rs = session_group.add_refresh_session(
        user_agent="Back-end 1.1", ip_addr=IPv4Address("192.168.1.1")
    )
    assert len(session_group) == 1

    session_group.remove_refresh_session(rs.refresh_token)
    assert len(session_group) == 0

    rs = RefreshSession(
        session_group_id=session_group.aggregate_id,
        user_agent="Back-end 1.1",
        ip_addr=IPv4Address("192.168.1.1"),
        expires_at=time.time() - 60,
    )
    session_group.refresh_sessions.append(rs)
    try:
        session_group.refresh_session(refresh_token=rs.refresh_token)
    except Exception as e:
        assert isinstance(e, RefreshSessionIsExpired)
