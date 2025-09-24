from abc import ABC

from src.core.interfaces.repository import AbstractRepository

#add model attr
class ProfilesRepository(AbstractRepository, ABC):
    pass

class RelationshipsGroupsRepository(AbstractRepository, ABC):
    pass

class FollowRequestsRepository(AbstractRepository, ABC):
    pass