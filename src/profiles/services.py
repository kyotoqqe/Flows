import uuid
from typing import Optional, BinaryIO

from src.core.domain.value_obj import Image
from src.core.domain.service import ImageClenupService
from src.core.s3.client import S3Client

from src.profiles.interfaces.units_of_work import ProfilesUnitOfWork, RelationshipsGroupsUnitOfWork, FollowRequestsUnitOfWork
from src.profiles.domain.entities import Profile, RelationshipGroup
from src.profiles.domain.value_obj import ProfileType, FollowRequest
from src.profiles.utils import get_checksum


class ProfileService:

    def __init__(self, uow: ProfilesUnitOfWork):
        self._uow = uow

    async def create_profile(self, user_id: int, username: str):
        async with self._uow:
            profile = Profile(
                user_id=user_id,
                username=username,
                profile_type=ProfileType.public
            )

            profile = await self._uow.profiles.add(
                profile,
                exclude = {"id", "created_at", "updated_at"}
            )
            
            await self._uow.commit()
            return profile
    
    async def update_profile(self, user_id: int, avatar:Optional[BinaryIO] = None,**kwargs):
        async with self._uow:
            if kwargs:
                profile = await self._uow.profiles.update(model=kwargs, user_id=user_id)
            else:
                profile = await self._uow.profiles.get(user_id=user_id)

            if not profile:
                raise #ProfileDontExist
            
            if avatar:
                #temporary
                s3 = S3Client("flows-app-avatars-bucket")
                print(profile.image)
                if profile.image:
                    old_image = profile.image
                    old_image.ref_count -= 1
                    print(old_image.ref_count)
                    if not ImageClenupService._check_usage(old_image):
                        #delete from s3
                        await self._uow.images.delete(id=old_image.id)
                        await s3.delete_file(old_image.key)
              
                checksum = get_checksum(avatar)
                image = await self._uow.images.get(checksum=checksum)
                
                if not image:
                    image = Image(
                        key=str(uuid.uuid4()),
                        checksum=checksum,
                        alt_text="Profile image"
                    )
                    image = await self._uow.images.add(
                        model=image,
                        exclude={"created_at", "updated_at"}
                    )
                    await s3.upload_file(filename=image.key, file=avatar)

                profile.avatar_id = image.id
                    
    
            await self._uow.commit()
            return profile

class RelationshipGroupService:
    #refactoring to different uows
    def __init__(self, uow: ProfilesUnitOfWork, redis_uow: Optional[FollowRequestsUnitOfWork] = None):
        self._uow = uow
        #test change this its horrible
        self._redis_uow = redis_uow  
    
    async def follow(self, follower_user_id: int, following_id: int):
        async with self._uow:

            follower = await self._uow.profiles.get(user_id=follower_user_id)
            following = await self._uow.profiles.get(id=following_id)

            if not follower or not following:
                raise ValueError("Cannot form a relationship with a non-existent subscriber or subscribers")#create custom
            
            if follower.id == following.id:
                raise ValueError("You can't subscribe to yourself") #create custom
            
            #переделать на строки чтобы не возникало колизий 
            relation_id = "-".join(sorted(map(str,[follower.id,following.id])))
            relationship_group = await self._uow.relationships_groups.get(relation_id=relation_id)

            if not relationship_group:
                relationship_group = RelationshipGroup(relation_id=relation_id)
                await self._uow.relationships_groups.add(relationship_group)
            relationship_group.profiles = [follower, following]
        
            relationship = relationship_group.follow(follower_id=follower.id, following_id=following_id)
            await self._uow.relationships_groups.update(relationship_group)
            await self._uow.commit()

            return relationship 
        
    async def unfollow(self, follower_user_id: int, following_id: int):
        async with self._uow:
            follower = await self._uow.profiles.get(user_id=follower_user_id)
            following = await self._uow.profiles.get(id=following_id)

            if not follower or not following:
                raise ValueError("Cannot form a relationship with a non-existent subscriber or subscribers")#create custom
            
            if follower.id == following.id:
                raise ValueError("You can't unfollow to yourself") #create custom
            
            relation_id = "-".join(sorted(map(str,[follower.id, following.id])))
            relationship_group = await self._uow.relationships_groups.get(relation_id=relation_id)

            if not relationship_group:
                raise ValueError("Relationship group doesnt exist") #create custom
            
            relationship = relationship_group.unfollow(follower.id, following.id)

            await self._uow.relationships_groups.update(relationship_group)
            await self._uow.commit()
            
            return relationship
    
    async def block(self, follower_user_id: int, following_id: int):
        async with self._uow:
            follower = await self._uow.profiles.get(user_id=follower_user_id)
            following = await self._uow.profiles.get(id=following_id)

            if not follower or not following:
                raise ValueError("Cannot form a relationship with a non-existent subscriber or subscribers")#create custom
            
            if follower.id == following.id:
                raise ValueError("You can't block to yourself") #create custom
            
            relation_id = "-".join(sorted(map(str, [follower.id, following.id])))
            relationship_group = await self._uow.relationships_groups.get(relation_id=relation_id)

            if not relationship_group:
                relationship_group = RelationshipGroup(relation_id=relation_id)
                await self._uow.relationships_groups.add(relationship_group)
            
            relation = relationship_group.block(follower.id, following.id)
            await self._uow.relationships_groups.update(relationship_group)

            await self._uow.commit()
            return relation

    async def unblock(self, follower_user_id: int, following_id: int):
        async with self._uow:
            follower = await self._uow.profiles.get(user_id=follower_user_id)
            following = await self._uow.profiles.get(id=following_id)

            if not follower or not following:
                raise ValueError("Cannot form a relationship with a non-existent subscriber or subscribers")#create custom
            
            if follower.id == following.id:
                raise ValueError("You can't unblock to yourself") #create custom
            
            relation_id = "-".join(sorted(map(str, [follower.id, following.id])))
            relationship_group = await self._uow.relationships_groups.get(relation_id=relation_id)

            if not relationship_group:
                raise ValueError("Relationship group doesnt exist") #create custom
            
            relation = relationship_group.unblock(follower.id, following.id)
            await self._uow.relationships_groups.update(relationship_group)

            await self._uow.commit()
            return relation
        
    async def follow_request(self, follower_user_id: int, following_id: int):
        async with self._uow:
            follower = await self._uow.profiles.get(user_id=follower_user_id)
            following = await self._uow.profiles.get(id=following_id)
            print(follower)
            print(following)
            if not follower or not following:
                raise ValueError("Cannot form a relationship with a non-existent subscriber or subscribers")#create custom
            
            if follower.id == following.id:
                raise ValueError("You can't unblock to yourself") #create custom
            
            relation_id = "-".join(sorted(map(str, [follower.id, following.id])))
            relationship_group = await self._uow.relationships_groups.get(relation_id=relation_id)

            if not relationship_group:
                relationship_group = RelationshipGroup(relation_id=relation_id)
                await self._uow.relationships_groups.add(relationship_group)
            
            request = relationship_group.create_follow_request(follower_id=follower.id, following_id=following.id)
            async with self._redis_uow:
                await self._redis_uow.follow_requests.add(request)

                await self._redis_uow.commit()
            await self._uow.commit()
            return request
    
    async def accept_follow_request(self, follower_user_id: int, following_id: int):
        async with self._uow:  
            follower = await self._uow.profiles.get(user_id=follower_user_id)
            following = await self._uow.profiles.get(id=following_id)
           
            if not follower or not following:
                raise ValueError("Cannot form a relationship with a non-existent subscriber or subscribers")#create custom
            
            if follower.id == following.id:
                raise ValueError("You can't unblock to yourself") #create custom
            
            relation_id = "-".join(sorted(map(str, [follower.id, following.id])))
            relationship_group = await self._uow.relationships_groups.get(relation_id=relation_id)

            if not relationship_group:
                raise ValueError("Relationship group doesnt exist") #create custom
            
            async with self._redis_uow:
                request = await self._redis_uow.follow_requests.get(scalar = True, follower_id=following_id, following_id=follower.id)
            
                if not request:
                    raise ValueError("Request dont exist")

                relation = relationship_group.accept_follow_request(request)
            
                await self._redis_uow.follow_requests.update(request)
                #await self._redis_uow.follow_requests.delete(follower_id=follower_user_id, following_id=following_id)
                await self._redis_uow.commit()

            #await self._uow.relationships_groups.update(relationship_group)
            await self._uow.commit()
            return request
    
    async def cancel_follow_request(self, follower_user_id: int, following_id: int):
        async with self._uow:
            follower = await self._uow.profiles.get(user_id=follower_user_id)
           
            if not follower:
                raise ValueError("Cannot delete a request with a non-existent subscriber or subscribers")#create custom
            
            async with self._redis_uow:
                await self._redis_uow.follow_requests.delete(follower_id = follower.id, following_id=following_id)
                await self._redis_uow.commit()
    

            
