from dataclasses import dataclass
from typing import Set, List
from datetime import datetime

@dataclass
class Role:
    pass

@dataclass
class Member:
    pass

@dataclass
class Location:
    pass

@dataclass
class Event:
    pass

class Organization:
    version_num: int
    id: int
    name: str
    description: str
    owner_id: int
    roles: Set[Role]
    members: List[Member]
    locations: List[Location]
    events: List[Event]
    created_at: datetime
    updated_at: datetime