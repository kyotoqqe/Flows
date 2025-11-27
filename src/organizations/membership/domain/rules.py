from src.core.domain.rules import BaseRule

from src.organizations.membership.domain.value_obj import MemberRole

class IsCanAddMembers(BaseRule):
    __message = "You must either have the appropriate permission to add members or be the owner of the organization."

    def __init__(self, member):
        self.member = member

    def is_broken(self) -> bool:
        return not self.member.can_invite_members and self.member.role != MemberRole.owner
    
class IsHasAuthorityOver(BaseRule):
    __message = "You don't have permissions to interact with this member"

    def __init__(self, actor, target):
        self.actor = actor
        self.target = target

    def is_broken(self):
        if self.actor.role == MemberRole.member:
            return True
        
        if self.actor.role == MemberRole.admin and (self.target.role in [MemberRole.admin, MemberRole.owner]):
            return True
        
        return False

class IsOwner(BaseRule):
    __message = "Only owner of the organization can transfer this role"

    def __init__(self, actor):
        self.actor = actor
    
    def is_broken(self):
        return self.actor.role != MemberRole.owner

class IsCanChangeMemberPermission(BaseRule):
    __message = "You can’t change this permission for another member because you don’t have this permission yourself."

    def __init__(self, actor, permission: str):
        self.actor = actor
        self.permission = permission
    
    def is_broken(self):
        actor_permission_val = getattr(self.actor, self.permission)
        return not actor_permission_val

class IsCanChangeMemberRole(BaseRule):
    __message = "You can’t assign someone a role higher than your own or make someone else the owner."

    def __init__(self, actor, target, role):
        self.actor = actor
        self.target = target
        self.role = role

    def is_broken(self):
       if self.role == MemberRole.owner:
           return True

        