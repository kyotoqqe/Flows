from dataclasses import asdict

from src.core.interfaces.handlers import AbstractCommandHandler
from src.core.domain.exceptions import EntityAlreadyExist, EntityNotFound

from src.organizations.organizations.domain.events import OrganizationCreated

from src.organizations.membership.interfaces.units_of_work import MembershipsUnitOfWork
from src.organizations.membership.domain.entities import Membership, Member
from src.organizations.membership.domain.value_obj import MemberRole
from src.organizations.membership.application.commands import CreateMember, DeleteMember, ChangeOwner, UpdateMember


class CreateMembershipHandler(AbstractCommandHandler):
    
    def __init__(self, uow: MembershipsUnitOfWork):
        self.uow = uow

    async def __call__(self, event: OrganizationCreated):
        async with self.uow:
            membership = await self.uow.memberships.get(organization_id=event.organizaton_id)

            if membership:
                raise EntityAlreadyExist(model=Membership, organization_id=event.organizaton_id)
            #move to domain
            membership = Membership(
                organization_id=event.organizaton_id,
                events=[],
            )
            membership.version_num += 1
            membership = await self.uow.memberships.add(membership, exclude={"id", "events"})
            await self.uow.commit()

            #create seperate handler
            membership = await self.uow.memberships.get(organization_id=event.organizaton_id)
            membership.events = []
            owner = Member(
                profile_id=event.owner_id,
                description="Organization owner",
                membership_id=membership.id,
                role=MemberRole.owner,
                can_change_organization_info=True,
                can_invite_members=True,
                can_create_shows=True,
                can_add_venue_requests=True
            )
            membership.members.append(owner)
            await self.uow.memberships.update(await membership.to_dict(exclude={"events"}), organization_id=event.organizaton_id)
            await self.uow.commit()
            return membership
        
class CreateMemberHandler(AbstractCommandHandler):
    def __init__(self, uow: MembershipsUnitOfWork):
        self.uow = uow

    async def __call__(self, command: CreateMember):
        async with self.uow:
            membership = await self.uow.memberships.get(id=command.membership_id)

            if not membership:
                raise EntityNotFound(Membership, id=command.membership_id)
            
            membership.events = []
            inviter = membership._check_member_existence(command.inviter_id)
            if not inviter:
                return EntityNotFound(Member, profile_id=command.inviter_id)
            
            new_member = membership.add_member(
                inviter=inviter,
                owner_id=command.invitee_id,
                description=command.description,
                can_change_organization_info=command.can_change_organization_info,
                can_invite_members=command.can_invite_members,
                can_create_shows=command.can_create_shows,
                can_add_venue_requests=command.can_add_venue_requests
            ) 
            if not new_member:
                raise EntityAlreadyExist(Member, owner_id=command.invitee_id)

            await self.uow.memberships.update(await membership.to_dict(exclude={"id", "organization_id", "events"}), id=command.membership_id)
            await self.uow.commit()
            return new_member 
            
class DeleteMemberHandler(AbstractCommandHandler):
    
    def __init__(self, uow: MembershipsUnitOfWork):
        self.uow = uow

    async def __call__(self, command: DeleteMember):
        async with self.uow:
            membership = await self.uow.memberships.get(id=command.membership_id)

            if not membership:
                raise EntityNotFound(Membership, id=command.membership_id)
            
            membership.events = []
            actor = membership._check_member_existence(command.actor_id)
            if not actor:
                return EntityNotFound(Member, profile_id=command.actor_id)
            
            deleted_member = membership.delete_member(actor, command.target_id)
            if not deleted_member:
                raise EntityNotFound(Member, target_id=command.target_id)
            
            await self.uow.commit()
            return deleted_member
        
class ChangeOwnerHandler(AbstractCommandHandler):

    def __init__(self, uow: MembershipsUnitOfWork):
        self.uow = uow

    async def __call__(self, command: ChangeOwner):
        async with self.uow:
            membership = await self.uow.memberships.get(id=command.membership_id)

            if not membership:
                raise EntityNotFound(Membership, id=command.membership_id)
            
            membership.events = []
            actor = membership._check_member_existence(command.actor_id)
            if not actor:
                return EntityNotFound(Member, profile_id=command.actor_id)
            
            new_owner = membership.change_owner(actor, command.target_id)
            if not new_owner:
                raise EntityNotFound(Member, target_id=command.target_id)
            
            await self.uow.commit()
            return new_owner
        
class UpdateMemberHandler(AbstractCommandHandler):
    
    def __init__(self, uow: MembershipsUnitOfWork):
        self.uow = uow
    
    async def __call__(self, command: UpdateMember):
        async with self.uow:
            membership = await self.uow.memberships.get(id=command.membership_id)

            if not membership:
                raise EntityNotFound(Membership, id=command.membership_id)
            
            membership.events = []
            actor = membership._check_member_existence(command.actor_id)
            if not actor:
                return EntityNotFound(Member, profile_id=command.actor_id)
            
            update_data = asdict(command)
            del update_data["membership_id"]
            del update_data["actor_id"]
            updated_member = membership.update_member(**update_data)
            updated_member = membership.change_owner(actor, command.target_id)
            if not updated_member:
                raise EntityNotFound(Member, target_id=command.target_id)
            
            await self.uow.commit()
            return updated_member