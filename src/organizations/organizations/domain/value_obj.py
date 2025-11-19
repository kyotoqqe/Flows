from dataclasses import dataclass

from src.core.domain.value_obj import ValueObj

@dataclass
class OrganizationRequest(ValueObj):
    name: str
    nickname: str
    owner_id: int