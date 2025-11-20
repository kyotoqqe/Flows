from abc import ABC

from src.core.interfaces.units_of_work import AbstractUnitOfWork
from src.core.interfaces.repository import TrackingRepository

from src.organizations.organizations.interfaces.repository import OrganizationsRepository, OrganizationRequestsRepository

class OrganizationsUnitOfWork(AbstractUnitOfWork, ABC):
    organizations: TrackingRepository

class OrganizationRequestsUnitOfWork(AbstractUnitOfWork, ABC):
    organization_requests: OrganizationRequestsRepository