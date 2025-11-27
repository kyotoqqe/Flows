from abc import ABC
from dataclasses import dataclass, asdict
from typing import Optional, Set, Dict, Any

@dataclass
class AbstractModel(ABC):

    async def to_dict(
        self,
        exclude:Optional[Set[str]] = None,
        include:Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        
        data: Dict[str, Any] = asdict(self)

        if exclude:
            for field in exclude:
                del data[field]
        
        if include:
            data.update(include)
        
        return data
    
    def __str__(self):
        return self.__class__.__name__