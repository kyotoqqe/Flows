import datetime
import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class Command:
    correlation_id: UUID = field(default_factory=uuid.uuid4)
    timestamp: int = int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000)
    command_id: UUID = field(default_factory=uuid.uuid4)
