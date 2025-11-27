from dataclasses import dataclass, field
from typing import Optional, List

from src.core.domain.entities import AggregateRoot
from src.core.domain.events import DomainEvent

from src.organizations.organizations.domain.value_obj import Venue

@dataclass(eq=False, kw_only=True)
class Organization(AggregateRoot):
    name: str
    nickname: str
    owner_id: int
    description: Optional[str] = None
    venues: List[Venue]
    
    #Venues
    def create_venue(self):
        pass

    def change_venue(self):
        pass

    def deactivate_venue(self):
        pass

