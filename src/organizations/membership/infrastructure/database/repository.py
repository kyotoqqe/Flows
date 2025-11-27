from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from src.core.database.interfaces.repository import SQLAlchemyRepository

from src.organizations.membership.interfaces.repository import MembershipsRepository
from src.organizations.membership.domain.entities import Membership


class SQLAlchemyMembershipsRepository(SQLAlchemyRepository, MembershipsRepository):
    model=Membership

    async def get(self, *filter, **filter_by):
        stmt = select(self.model).options(selectinload(self.model.members))\
            .filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()