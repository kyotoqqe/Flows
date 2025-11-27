from pydantic import BaseModel 
from typing import Optional

from src.organizations.membership.domain.value_obj import MemberRole

class CreateMemberSchema(BaseModel):
    invitee_id: int
    description: str
    membership_id: int
    can_change_organization_info: bool
    can_invite_members: bool
    can_create_shows: bool
    can_add_venue_requests: bool

class DeleteMemberSchema(BaseModel):
    membership_id: int
    target_id: int

class ChangeOwnerSchema(BaseModel):
    membership_id: int
    target_id: int

class UpdateMemberSchema(BaseModel):
    membership_id: int
    target_id: int
    membership_id: int
    role: Optional[MemberRole] = None
    description: Optional[str] = None
    can_change_organization_info: Optional[bool] = None
    can_invite_members: Optional[bool] = None
    can_create_shows: Optional[bool] = None
    can_add_venue_requests: Optional[bool] = None