from pydantic import BaseModel, model_validator

from src.profiles.domain.value_obj import ProfileType

from typing import Optional, Self
from datetime import datetime

class ProfileSchema(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_id: int
    username: str
    profile_type: ProfileType
    created_at: datetime 
    updated_at: datetime 

class ProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    profile_type: Optional[ProfileType] = None


