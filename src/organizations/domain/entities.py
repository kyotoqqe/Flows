from dataclasses import dataclass, field
from typing import Optional, List

from src.core.domain.entities import AggregateRoot
from src.core.domain.events import DomainEvent


@dataclass
class Organization(AggregateRoot):
    name: str
    nickname: str
    owner_id: int
    description: Optional[str] = None
    events: List[DomainEvent] = field(default_factory=list)