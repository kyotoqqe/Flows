from dataclasses import dataclass
from typing import Optional
from enum import Enum

from src.core.domain.value_obj import ValueObj

@dataclass
class OrganizationRequest(ValueObj):
    name: str
    nickname: str
    owner_id: int


class VenueStatus(Enum):
    pending = "Pending"
    active = "Active"
    closed = "Closed"

@dataclass
class Venue(ValueObj):
    name: str
    description: Optional[str]
    organization_id: int
    country: str
    city: str
    street: str
    building: Optional[str]
    status: VenueStatus
    latitude: float
    longitude: float