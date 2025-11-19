from abc import ABC

from src.core.interfaces.repository import AbstractRepository

class OrganizationsRepository(AbstractRepository, ABC):
    pass

class OrganizationRequestsRepository(AbstractRepository, ABC):
    pass