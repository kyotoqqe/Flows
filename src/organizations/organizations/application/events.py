from dataclasses import dataclass

from src.core.domain.events import DomainEvent

@dataclass
class OrganizationRequestCreated(DomainEvent):
    pass