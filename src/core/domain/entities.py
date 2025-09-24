from dataclasses import field, dataclass
from src.core.interfaces.model import AbstractModel

@dataclass(eq=False)
class Entity(AbstractModel):
    id: int = field(init=False)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return other.id == self.id
        return False
    
    def __hash__(self):
        return hash(self.id)
#fix this

class AggregateRoot(AbstractModel):
    pass

