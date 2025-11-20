from src.core.interfaces.handlers import AbstractCommandHandler
from src.core.domain.exceptions import EntityAlreadyExist

from src.organizations.organizations.domain.events import OrganizationCreated

from src.organizations.membership.interfaces.units_of_work import MembershipsUnitOfWork
from src.organizations.membership.domain.entities import Membership, Member
from src.organizations.membership.domain.value_obj import MemberRole

class CreateMembershipHandler(AbstractCommandHandler):
    
    def __init__(self, uow: MembershipsUnitOfWork):
        self.uow = uow

    async def __call__(self, event: OrganizationCreated):
        async with self.uow:
            membership = await self.uow.memberships.get(organization_id=event.organizaton_id)

            if membership:
                return EntityAlreadyExist(model=Membership, organization_id=event.organizaton_id)
            
            owner = Member(
                profile_id=event.owner_id,
                description="Organization owner",
                role=MemberRole.owner,
                can_change_organization_info=True,
                can_invite_members=True,
                can_create_shows=True,
                can_add_venue_requests=True
            )

            membership = Membership(
                organization_id=event.organizaton_id,
                owner=owner,
            )
            membership.members.append(owner)
            membership.version_num += 1

            await self.uow.memberships.add(membership, exclude={"id", "events"})
            await self.uow.commit()
            return membership