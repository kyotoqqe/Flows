import uuid

from shared.application.exceptions import MappedEventMismatchException
from shared.tests.fixtures.application.events import UserCreated
from shared.tests.fixtures.domain.events import EmptyEvent
from shared.tests.fixtures.domain.events import UserCreated as DomainUserCreated


def test_event_transformation():
    domain_event = DomainUserCreated(
        id=1, username="user", email="user@gmail.com", is_active=True, password_hash="some_hash"
    )

    integration_event = UserCreated.build(domain_event=domain_event, correlation_id=uuid.uuid4())

    assert isinstance(integration_event, UserCreated)


def test_event_transformation_failed():
    domain_event = EmptyEvent()

    try:
        UserCreated.build(domain_event=domain_event, correlation_id=uuid.uuid4())
    except Exception as e:
        assert isinstance(e, MappedEventMismatchException)
