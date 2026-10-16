import datetime
import uuid
from dataclasses import asdict, dataclass, field, fields
from typing import ClassVar
from uuid import UUID

from shared.application.exceptions import MappedEventMismatchException
from shared.domain.events import DomainEvent

METADATA_FIELDS = ["correlation_id", "timestamp", "event_id", "version"]


@dataclass(frozen=True, kw_only=True)
class IntegrationEvent:
    correlation_id: UUID
    timestamp: int = field(
        default_factory=lambda: int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000)
    )
    event_id: UUID
    mapped_event: ClassVar[type[DomainEvent] | None] = None
    version: int = field(default=1)

    @classmethod
    def build_from(cls, domain_event: DomainEvent, correlation_id: UUID | None):
        if cls.mapped_event and not isinstance(domain_event, cls.mapped_event):
            raise MappedEventMismatchException(
                f"Integration event '{cls.__name__}' expects domain event "
                f"'{cls.mapped_event.__name__}', got '{type(domain_event).__name__}'."
            )

        if not correlation_id:
            correlation_id = uuid.uuid4()

        domain_event_data = asdict(domain_event)
        payload = {}

        for f in fields(cls):
            if f.name in domain_event_data:
                payload[f.name] = domain_event_data[f.name]

        return cls(
            correlation_id=correlation_id,
            **payload,
        )

    @property
    def payload(self):
        res = {}

        for f in fields(self):
            if f.name not in METADATA_FIELDS:
                res[f.name] = getattr(self, f.name)

        return res
