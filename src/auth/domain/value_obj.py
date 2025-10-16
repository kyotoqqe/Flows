from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime

from src.core.domain.value_obj import ValueObj

@dataclass
class RefreshSession(ValueObj):
    user_id: int
    token:UUID
    expires_in:int
    created_at: datetime = field(init=False)
