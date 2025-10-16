from dataclasses import dataclass

from src.core.domain.entities import Entity
from src.core.domain.mixins import TimeStampMixin

@dataclass(eq=False)
class User(Entity, TimeStampMixin):
    email:str
    password:str
    active: bool = False
    
    def activate(self):
        self.active = True
