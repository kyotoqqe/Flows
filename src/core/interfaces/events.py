from abc import ABC
from dataclasses import dataclass

@dataclass
class AbstractEvent(ABC):
    pass

@dataclass
class ApplicationEvent(AbstractEvent):
    pass

@dataclass
class ExternalEvent(AbstractEvent):
    pass