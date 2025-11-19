from dataclasses import asdict

from src.core.interfaces.handlers import AbstractCommandHandler, AbstractEventHandler
from src.core.messagebus import MessageBus
from src.core.domain.exceptions import EntityAlreadyExist

from src.organizations.organizations.application.commands import CreateOrganizationRequest, CheckOrganizationExistence, DeleteOrganizationRequest
from src.organizations.organizations.interfaces.units_of_works import OrganizationRequestsUnitOfWork, OrganizationsUnitOfWork
from src.organizations.organizations.domain.value_obj import OrganizationRequest
from src.organizations.organizations.domain.entities import Organization

from src.payments.application.events import OrganizationPaymentSucceeded

class CreateOrganizationRequestHandler(AbstractCommandHandler):

    def __init__(self, 
                 uow: OrganizationRequestsUnitOfWork, 
                 **kwargs):
        self.uow = uow
        self.kwargs = kwargs

    async def __call__(self, command: CreateOrganizationRequest, messagebus: MessageBus):
        async with self.uow:
            check_cmd = CheckOrganizationExistence(nickname=command.nickname)
            await messagebus.handle(check_cmd)
            if messagebus.command_result:
                raise EntityAlreadyExist(model=Organization, nickname=command.nickname)
            
            request = OrganizationRequest(**asdict(command))

            try:
                await self.uow.organization_requests.add(request, **self.kwargs)
            except ValueError:
                raise EntityAlreadyExist(model=OrganizationRequest, **asdict(command))
            await self.uow.commit()
            return request

class CheckOrganizationExistenceHandler(AbstractCommandHandler):
    
    def __init__(self, uow: OrganizationsUnitOfWork):
        self.uow = uow
    
    async def __call__(self, command: CheckOrganizationExistence):
        async with self.uow:
            organization = await self.uow.organizations.get(**asdict(command))
            
            if organization:
                return True
            
            return False

class CreateOrganizationHandler(AbstractEventHandler):
    
    def __init__(self, uow: OrganizationsUnitOfWork):
        self.uow = uow

    async def __call__(self, event: OrganizationPaymentSucceeded, messagebus: MessageBus):
        async with self.uow:
            model = Organization(**asdict(event))
            model.owner_id = int(model.owner_id)
            organization = await self.uow.organizations.add(model, exclude={"id", "version_num", "events"})

            await self.uow.commit()
            await messagebus.handle(
                DeleteOrganizationRequest(model.name, model.nickname)
            )
            return organization


class DeleteOrganizationRequestHandler(AbstractCommandHandler):
    
    def __init__(self, uow: OrganizationRequestsUnitOfWork):
        self.uow = uow

    async def __call__(self, command: DeleteOrganizationRequest):
        async with self.uow:
            await self.uow.organization_requests.delete(**asdict(command))
            await self.uow.commit()

