from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update

from typing import Optional, Union, Dict

from src.core.interfaces.repository import AbstractRepository
from src.core.domain.entities import AbstractModel



class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, *filter, **filter_by) -> Optional[AbstractModel]:
        stmt = select(self.model).filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def add(self, model: AbstractModel, exclude: Optional[set] = None) -> AbstractModel:
        stmt = insert(self.model).values(**await model.to_dict(exclude=exclude)).returning(self.model) #exclude={"id"}
        res = await self.session.execute(stmt)
        return res.scalar_one()
        #add logging and catching exception
    
    async def delete(self, *filter, **filter_by):
        stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)

    async def update(self, model: Union[AbstractModel, Dict], *filter, **filter_by) -> Optional[AbstractModel]:  
        if isinstance(model, AbstractModel):
            model = await model.to_dict()
            
        stmt =  update(self.model)\
            .filter(*filter).filter_by(**filter_by)\
            .values(**model)\
            .returning(self.model) #exclude={"id"}
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def list(self, *filter, **filter_by) -> list[AbstractModel]: #add limit and offset for pagination
        stmt = select(self.model).filter(*filter).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalars().all()
    
