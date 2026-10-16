from uuid import uuid4


from shared.application.events.registry import integration_event_registry
from shared.application.exceptions import IntegrationEventAlreadyRegistrated
from shared.tests.fixtures.application.events import UserCreated


def test_integration_event_registration():
    integration_event_registry.register(UserCreated)

    assert len(integration_event_registry.registry) == 1


def test_event_instance_registration():
    try:
        event = UserCreated(
            type="UserCreated",
            correlation_id=uuid4(),
            event_id=uuid4(),
            timestamp=1788985727924,
            id=1,
            username="test",
            is_active=True,
        )
        integration_event_registry.register(event)
    except Exception as e:
        assert isinstance(e, TypeError)


def test_duplicate_event_registration():
    try:
        integration_event_registry.register(UserCreated)
        integration_event_registry.register(UserCreated)
    except Exception as e:
        assert isinstance(e, IntegrationEventAlreadyRegistrated)


def test_event_search():
    event = integration_event_registry.get("UserCreated")
    assert event == UserCreated
