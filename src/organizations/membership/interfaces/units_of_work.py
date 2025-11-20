from abc import ABC

from src.core.interfaces.units_of_work import AbstractUnitOfWork

from src.organizations.membership.interfaces.repository import MembershipsRepository

class MembershipsUnitOfWork(AbstractUnitOfWork, ABC):
    memberships: MembershipsRepository