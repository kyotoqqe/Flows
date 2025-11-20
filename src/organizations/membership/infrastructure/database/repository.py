from src.core.database.interfaces.repository import SQLAlchemyRepository

from src.organizations.membership.interfaces.repository import MembershipsRepository
from src.organizations.membership.domain.entities import Membership


class SQLAlchemyMembershipsRepository(SQLAlchemyRepository, MembershipsRepository):
    model=Membership