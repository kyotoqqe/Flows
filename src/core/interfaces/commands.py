from abc import ABC
from dataclasses import dataclass

@dataclass
class AbstractCommand(ABC):
    pass

@dataclass
class Command(AbstractCommand):
    pass

@dataclass
class ExternalCommand(AbstractCommand):
    pass