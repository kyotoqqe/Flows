from dataclasses import dataclass

from src.core.interfaces.events import AbstractEvent

@dataclass
class DomainEvent(AbstractEvent):
    pass