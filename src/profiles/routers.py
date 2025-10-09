from fastapi import APIRouter, Depends, UploadFile

from src.core.worker.tasks import execute, add, divide

from src.auth.schemas import UserSchema
from src.auth.dependencies import get_active_user

from src.profiles.schemas import ProfileUpdateSchema
from src.profiles.services import ProfileService, RelationshipGroupService
from src.profiles.units_of_work import SQLAlchemyProfilesUnitOfWork, SQLAlchemyRelationshipsGroupsUnitOfWork, RedisFollowRequestsUnitOfWork
from src.profiles.dependencies import Checker


from typing import Annotated, Optional

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles Managment"]
)

@router.post("/update")
async def update_profile(
    user: Annotated[UserSchema, Depends(get_active_user)],
    profile_data:ProfileUpdateSchema = Depends(Checker(pydantic_model=ProfileUpdateSchema)),
    avatar: Optional[UploadFile] = None
    ):
    res1 = execute.delay(add, 5, 2)
    res2 = execute.delay(divide, 10, 2)
    print(res1.get())
    print(res2.get())
    if avatar:
        avatar = avatar.file
    service = ProfileService(uow=SQLAlchemyProfilesUnitOfWork())
    return await service.update_profile(user_id=user.id, avatar=avatar, **profile_data.model_dump(exclude_unset=True))

@router.post("/follow")
async def follow_profile(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int 
):
    service = RelationshipGroupService(uow=SQLAlchemyProfilesUnitOfWork())
    return await service.follow(follower_user_id=user.id, following_id=following_id)

@router.post("/unfollow")
async def unfollow_profile(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(uow=SQLAlchemyProfilesUnitOfWork())
    return await service.unfollow(follower_user_id=user.id, following_id=following_id)

@router.post("/block")
async def block_profile(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(uow=SQLAlchemyProfilesUnitOfWork())
    return await service.block(follower_user_id=user.id, following_id=following_id)

@router.post("/unblock")
async def unblock_profile(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(uow=SQLAlchemyProfilesUnitOfWork())
    return await service.unblock(follower_user_id=user.id, following_id=following_id)

@router.post("/follow/request")
async def follow_request(
    #change on user
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(uow=SQLAlchemyProfilesUnitOfWork(), redis_uow=RedisFollowRequestsUnitOfWork())
    return await service.follow_request(follower_user_id=user.id, following_id=following_id)

@router.post("/accept/follow/request")
async def accept_follow_request(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(uow=SQLAlchemyProfilesUnitOfWork(), redis_uow=RedisFollowRequestsUnitOfWork())
    return await service.accept_follow_request(follower_user_id=user.id, following_id=following_id)

@router.delete("/cancel/follow/request")
async def cancel_follow_request(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(
        uow=SQLAlchemyProfilesUnitOfWork(),
        redis_uow=RedisFollowRequestsUnitOfWork()
    )

    return await service.cancel_follow_request(follower_user_id=user.id, following_id=following_id)

@router.delete("/decline/follow/request")
async def decline_follow_request(
    user: Annotated[UserSchema, Depends(get_active_user)],
    following_id: int
):
    service = RelationshipGroupService(uow=RedisFollowRequestsUnitOfWork())
    return await service.cancel_follow_request(follower_user_id=following_id, following_id=user.id) 