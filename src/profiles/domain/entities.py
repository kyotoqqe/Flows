from dataclasses import dataclass, field

from src.core.domain.entities import Entity, AggregateRoot
from src.profiles.domain.value_obj import ProfileType, Relationship, FollowRequest

from typing import Optional, List
from datetime import datetime

@dataclass(eq=False)
class RelationshipGroup(AggregateRoot):
    relation_id: str
    version_num: int = 0

    def _search_profile(self, profile_id: int):
        for profile in self.profiles:
            if profile.id == profile_id:
                return profile

    def follow(self, follower_id: int, following_id: int):
        #refactor this shit add invariant if you block user, you cant follow him and raise error if profile private
        if len(self.relationships) == 0:
            follow = Relationship(
               follower_id = follower_id,
               following_id = following_id,
               relation_id= self.relation_id,
               is_followed = True
            )
            self.relationships.append(follow)
            self.version_num += 1
            return follow 

        relation = self.relationships[-1]
        if relation.follower_id == follower_id and relation.following_id == following_id:
            raise ValueError("Following does exist") #create custom
        
        if relation.is_blocked:
            raise ValueError("You can't follow an account that blocked you.")
        
        following = self._search_profile(following_id)

        if following.profile_type == ProfileType.private:
            raise ValueError("You can`t follow private profile without following request")
        
        follow = Relationship(
               follower_id = follower_id,
               following_id = following_id,
               relation_id= self.relation_id,
               is_followed = True
            )
        self.relationships.append(follow)
        self.version_num += 1
        return follow
    
    def _search_relation(self, follower_id: int, following_id: int):
        for i, relation in enumerate(self.relationships):
            if relation.follower_id == follower_id and relation.following_id == following_id:
                return (i, relation)
        #fix that
        return (None, None)
        #raise ValueError("Relationship doesnt exist")
    
    def _delete_if_empty_else_return(self, index: int, relationship: Relationship):
        if relationship.is_empty():
            return self.relationships.pop(index)
        return relationship
    
    def _unfollow(self, follower_id: int, following_id: int):
        i, relation = self._search_relation(follower_id, following_id)
        if relation:
            relation.is_followed = False
            relation = self._delete_if_empty_else_return(i, relation)
              
            return relation

    def unfollow(self, follower_id: int, following_id: int):
        relation = self._unfollow(follower_id, following_id)

        if relation:
            self.version_num += 1
        
        return relation

    def block(self, follower_id: int, following_id: int):
        try:
            _, relation = self._search_relation(follower_id, following_id)
        except ValueError:
            relation = Relationship(
                follower_id=follower_id,
                following_id=following_id,
                relation_id=self.relation_id,
            )
            self.relationships.append(relation)

        if relation:
            relation.is_blocked = True
            self._unfollow(follower_id, following_id)
            self._unfollow(following_id, follower_id)

            self.version_num += 1
            return relation

    def unblock(self, follower_id: int, following_id: int):
        i, relation = self._search_relation(follower_id, following_id)

        if relation:
            relation.is_blocked = False
            relation = self._delete_if_empty_else_return(i, relation)

            self.version_num += 1
            return relation

    def create_follow_request(self, follower_id: int, following_id: int):
        _, follower_relation = self._search_relation(follower_id, following_id)

        if follower_relation:
            if follower_relation.is_followed:
                raise ValueError("You already followed to this user")#create custom
            elif follower_relation.is_blocked:
                raise ValueError("You blocked this profile. To send a subscription request, you first need to unblock it.")

        _, following_relation = self._search_relation(follower_id=following_id, following_id=follower_id)

        if following_relation:
            if following_relation.is_blocked:
                raise ValueError("You can`t send follow request to profile which blocked you") #create custom
            return FollowRequest(
                follower_id=follower_id,
                following_id=following_id
            )
      
    def accept_follow_request(self, request: FollowRequest):
        if request.accepted:
            raise ValueError("Request already accepted")
        
        _, following_relation = self._search_relation(follower_id=request.following_id, following_id=request.follower_id)

        if following_relation:
            if following_relation.is_blocked:
                raise ValueError("In order to accept a subscriber, you first need to unblock him.")
            
        request.accepted = True
        relation = Relationship(
            relation_id=self.relation_id,
            follower_id=request.follower_id,
            following_id=request.following_id,
            is_followed=True
        )

        self.relationships.append(relation)
        return relation


@dataclass(eq=False)
class Profile(Entity):
    user_id: int
    username: str
    #create value obj from image
    #image_url: str
    profile_type: ProfileType = field(default=ProfileType.public)
    #move to separate mixin
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    