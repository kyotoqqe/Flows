from abc import ABC

from src.core.interfaces.units_of_work import AbstractUnitOfWork

from src.profiles.interfaces.repository import ProfilesRepository, RelationshipsGroupsRepository, FollowRequestsRepository

#temporary
from src.core.interfaces.repository import ImagesRepository

#refactoring
class ProfilesUnitOfWork(AbstractUnitOfWork, ABC):
    profiles: ProfilesRepository
    relationships_groups: RelationshipsGroupsRepository
    images: ImagesRepository

class RelationshipsGroupsUnitOfWork(AbstractUnitOfWork, ABC):
    relationships_groups: RelationshipsGroupsRepository

class FollowRequestsUnitOfWork(AbstractUnitOfWork, ABC):
    follow_requests: FollowRequestsRepository