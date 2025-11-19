from fastapi import APIRouter, Depends
from typing import Annotated

from src.core.messagebus import MessageBus

from src.auth.schemas import UserSchema
from src.auth.dependencies import get_active_user

from src.organizations.api.schemas import CreateOrganizationRequestSchema
from src.organizations.application.handlers import EVENT_HANDLERS_FOR_INJECTION, COMMAND_HANDLERS_FOR_INJECTION
from src.organizations.application.units_of_work import RedisOrganizationRequestsUnitOfWork
from src.organizations.application.commands import CreateOrganizationRequest
from src.organizations.infrastructure.rabbitmq.broker import OrganizationRabbitMQBroker

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)

@router.post("/request")
async def create_organization_request(
    #change on Auth domain call
    user: Annotated[UserSchema, Depends(get_active_user)],
    organization_request: CreateOrganizationRequestSchema
):
    messagebus = MessageBus(
        event_handlers=EVENT_HANDLERS_FOR_INJECTION,
        command_handlers=COMMAND_HANDLERS_FOR_INJECTION,
        broker=OrganizationRabbitMQBroker()
    )
    data = dict(**organization_request.model_dump())
    data["owner_id"] = user.id
    command = CreateOrganizationRequest(**data)
    await messagebus.handle(command)
    return messagebus.command_result