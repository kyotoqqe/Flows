from dataclasses import dataclass

from src.core.domain.events import DomainEvent

@dataclass
class OrganizationPaymentSucceeded(DomainEvent):
    name: str
    nickname: str
    owner_id: int