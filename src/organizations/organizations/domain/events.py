from dataclasses import dataclass

from src.core.domain.events import DomainEvent

@dataclass
class OrganizationCreated(DomainEvent):
    #maybe add more info
    organizaton_id: int
    owner_id: int