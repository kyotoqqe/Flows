from enum import Enum
from dataclasses import dataclass, field

from src.core.interfaces.model import AbstractModel

class ProfileType(Enum):
    public = "Public"
    private = "Private"

@dataclass
class Relationship(AbstractModel):
    follower_id: int
    following_id: int
    relation_id: int
    is_followed: bool = field(default=False)
    is_blocked: bool = field(default=False)

    def is_empty(self) -> bool:
        return False if self.is_followed or self.is_blocked else True

@dataclass
class FollowRequest(AbstractModel):
    follower_id: int
    following_id: int
    accepted: bool = field(default=False)

if __name__ == '__main__':
    r = Relationship(1, 2, "1-2", False, False)
    print(r.is_empty())