from fastapi import Form, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from typing import Annotated

from src.core.domain.exceptions import EntityNotFound

from src.auth.dependencies import get_active_user
from src.auth.schemas import UserSchema

from src.profiles.services import ProfileService
from src.profiles.units_of_work import SQLAlchemyProfilesUnitOfWork
from src.profiles.domain.entities import Profile
from src.profiles.schemas import ProfileSchema

class Checker:
    def __init__(self, pydantic_model: BaseModel):
        self.pydantic_model = pydantic_model

    def __call__(self, data: str = Form(...)):
        try:
            return self.pydantic_model.model_validate_json(data)
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=jsonable_encoder(e.errors())
            )
        
async def get_profile(user: Annotated[UserSchema, Depends(get_active_user)]) -> ProfileSchema:
    service = ProfileService(uow=SQLAlchemyProfilesUnitOfWork())
    profile = await service.get_profile_by_user_id(user_id=user.id)

    if not profile:
        raise EntityNotFound(model=Profile, user_id=user.id)
    
    return profile