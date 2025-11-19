from src.core.database.interfaces.repository import SQLAlchemyRepository

from src.organizations.interfaces.repository import OrganizationsRepository
from src.organizations.domain.entities import Organization

class SQLAlchemyOrganizationsRepository(SQLAlchemyRepository, OrganizationsRepository):
    model=Organization