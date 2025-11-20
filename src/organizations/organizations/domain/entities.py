from dataclasses import dataclass
from typing import Optional

from src.core.domain.entities import AggregateRoot


@dataclass
class Organization(AggregateRoot):
    name: str
    nickname: str
    owner_id: int
    description: Optional[str] = None