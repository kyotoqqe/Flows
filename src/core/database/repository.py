from src.core.database.interfaces.repository import SQLAlchemyRepository 
from src.core.interfaces.repository import ImagesRepository
from src.core.domain.value_obj import Image

class SQLAlchemyImageRepository(SQLAlchemyRepository, ImagesRepository):
    model=Image