import uuid
from dataclasses import dataclass, field, fields
from uuid import UUID


METADATA_FIELDS = ["event_id", "correlation_id"]


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid.uuid4)
    correlation_id: UUID = field(default_factory=uuid.uuid4)

    @property
    def payload(self):
        res = {}

        for f in fields(self):
            if f.name not in METADATA_FIELDS:
                res[f.name] = getattr(self, f.name)

        return res
