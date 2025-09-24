from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime

from src.core.domain.entities import Entity

@dataclass(eq=False)
class User(Entity):
    email:str
    #remave username field
    username:str
    password:str
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
    active: bool = False
    
    def activate(self):
        self.active = True

@dataclass
class RefreshSession(Entity):
    user_id: int
    token:UUID
    expires_in:int
    created_at: datetime = field(init=False)
