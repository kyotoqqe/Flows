from shared.application.events.events import IntegrationEvent
from shared.application.exceptions import IntegrationEventAlreadyRegistrated
from shared.domain.events import DomainEvent


class IntegrationEventRegistry:
    def __init__(self) -> None:
        self.registry: dict[str, type[IntegrationEvent]] = {}

    def register(self, event: type[IntegrationEvent]):
        if not isinstance(event, type):
            raise TypeError("Event must be passed as type not as object")

        if issubclass(event, IntegrationEvent):
            event_name = event.__name__
            if event_name not in self.registry:
                self.registry[event_name] = event
            else:
                raise IntegrationEventAlreadyRegistrated("Event with this name already registrated")

    def get(self, event_name: str) -> type[IntegrationEvent]:
        if event_name in self.registry:
            return self.registry[event_name]
        raise ValueError("Not found event with this name")

    def get_by_mapped_event(self, mapped_event: DomainEvent) -> type[IntegrationEvent]:
        for v in self.registry.values():
            if v.mapped_event is not None:
                if isinstance(mapped_event, v.mapped_event):
                    return v
        raise ValueError("Not found event with this name")


integration_event_registry = IntegrationEventRegistry()

# put your events here
