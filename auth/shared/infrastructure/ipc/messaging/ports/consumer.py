from abc import ABC, abstractmethod

from shared.application.events.registry import IntegrationEventRegistry, integration_event_registry


class AbstractConsumer(ABC):
    EVENT_REGISTRY: IntegrationEventRegistry = integration_event_registry

    def _get_event_or_command_from_message(self, payload: dict):
        type = payload["type"]
        correlation_id = payload["correlation_id"]
        timestamp = payload["timestamp"]
        event_id = payload["message_id"]

        try:
            event = self.EVENT_REGISTRY.get(type)
            return event(
                type=type,
                correlation_id=correlation_id,
                timestamp=timestamp,
                event_id=event_id,
                **payload["body"],
            )
        except ValueError:
            raise ValueError("Event or command not found")

    @abstractmethod
    async def consume(self):
        pass
