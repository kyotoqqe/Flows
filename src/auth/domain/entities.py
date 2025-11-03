from dataclasses import dataclass

from src.core.domain.entities import Entity
from src.core.domain.mixins import TimeStampMixin

from src.auth.domain.value_obj import UserRole

@dataclass(eq=False)
class User(Entity, TimeStampMixin):
    email:str
    password:str
    role: UserRole
    active: bool = False
    
    def activate(self):
        self.active = True
