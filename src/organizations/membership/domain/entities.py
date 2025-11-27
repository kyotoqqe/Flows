from dataclasses import dataclass, field
from typing import Optional

from src.core.domain.entities import AggregateRoot, Entity

from src.organizations.membership.domain.value_obj import MemberRole
from src.organizations.membership.domain.rules import IsCanAddMembers, IsHasAuthorityOver, IsOwner, IsCanChangeMemberPermission, \
    IsCanChangeMemberRole

#change on profile_id
@dataclass(eq=False)
class Member(Entity):
<<<<<<< Updated upstream
    profile_id: int
=======
    owner_id: int
    role: MemberRole
    membership_id: int
>>>>>>> Stashed changes
    description: Optional[str] = None
    role: MemberRole
    can_change_organization_info: bool = field(default=False)
    can_invite_members: bool = field(default=False) 
    can_create_shows: bool = field(default=False)
    can_add_venue_requests: bool = field(default=False)

@dataclass(eq=False, kw_only=True)
class Membership(AggregateRoot):
    organization_id: int

    def _check_member_existence(self, owner_id: int):
        for member in self.members:
            if member.owner_id == owner_id:
                return member
        
        return None

    def add_member(self,
                inviter: Member, 
                owner_id: int, 
                description: str, 
                can_change_organization_info: bool,
                can_invite_members: bool,
                can_create_shows: bool,
                can_add_venue_requests: bool,
                role: MemberRole = MemberRole.member,
            ):
        if self._check_member_existence(owner_id=owner_id):
            return None

        rule = IsCanAddMembers(inviter)
        if rule.is_broken():
            raise ValueError(rule.get_message()) #change on custom
        
        member = Member(
            owner_id=owner_id,
            description=description,
            membership_id=self.id,
            can_change_organization_info=can_change_organization_info,
            can_invite_members=can_invite_members,
            can_create_shows=can_create_shows,
            can_add_venue_requests=can_add_venue_requests,
            role=role
        )


        self.members.append(member)
        self.version_num += 1
        return member
    
    def delete_member(self,
            actor: Member,
            target_id: int            
            ):
        target = self._check_member_existence(owner_id=target_id)
        if not target:
            return None
        
        rule = IsHasAuthorityOver(actor=actor, target=target)
        if rule.is_broken():
            raise ValueError(rule.get_message())

        self.members.remove(target)
        self.version_num += 1
        return target
        

    def change_owner(self, 
                actor: Member,
                targer_id: int
            ):
        target: Member = self._check_member_existence(owner_id=targer_id)
        if not target:
            return None
        
        rule = IsOwner(actor)
        if rule.is_broken():
            raise ValueError(rule.get_message())
        
        target.role = MemberRole.owner
        target.can_change_organization_info = True
        target.can_invite_members = True
        target.can_create_shows = True
        target.can_add_venue_requests = True

        actor.role = MemberRole.admin
        self.version_num += 1
        return target
    
    def update_member(self,
                actor: Member,
                targer_id: int,
                role: Optional[MemberRole] = None,
                description: Optional[str] = None,
                can_change_organization_info: Optional[bool] = None,
                can_invite_members: Optional[bool] = None,
                can_create_shows: Optional[bool] = None,
                can_add_venue_requests: Optional[bool] = None,
            ):
        target: Member = self._check_member_existence(owner_id=targer_id)
        if not target:
            return None
        
        rule = IsHasAuthorityOver(actor=actor, target=target)
        if rule.is_broken():
            raise ValueError(rule.get_message())

        passed_args = {key:value for key, value in locals().items() if value is not None}
        for key, value in passed_args.items():
            rule = IsCanChangeMemberPermission(actor, key) if key != "role" else IsCanChangeMemberRole(actor, target, value)
            if rule.is_broken():
                raise ValueError(rule.get_message())
            
            setattr(target, key, value)
        
        return target