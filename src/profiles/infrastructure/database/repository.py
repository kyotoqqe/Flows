from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from src.core.database.interfaces.repository import SQLAlchemyRepository

from src.profiles.interfaces.repository import ProfilesRepository, RelationshipsGroupsRepository
from src.profiles.domain.entities import Profile, RelationshipGroup


class SQLAlchemyProfilesRepository(SQLAlchemyRepository, ProfilesRepository):
    model=Profile

    async def get(self, *filter, **filter_by):
        stmt = select(self.model)\
            .options(joinedload(self.model.image))\
            .filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

class SQLAlchemyRelationshipsGroupsRepository(SQLAlchemyRepository, RelationshipsGroupsRepository):
    model=RelationshipGroup

    async def get(self, *filter, **filter_by):
        stmt = select(self.model)\
            .options(selectinload(self.model.relationships))\
            .filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()