from dataclasses import field, dataclass

from src.core.interfaces.model import AbstractModel
from src.core.domain.mixins import BusinessRuleValidationMixin

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
@dataclass(kw_only=True)
class AggregateRoot(Entity, BusinessRuleValidationMixin):
    version_num: int

