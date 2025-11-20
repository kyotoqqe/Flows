from fastapi import APIRouter, Depends
from typing import Annotated

from src.core.messagebus import MessageBus

from src.profiles.dependencies import get_profile
from src.profiles.schemas import ProfileSchema

from src.organizations.organizations.api.schemas import CreateOrganizationRequestSchema
from src.organizations import DOMAIN_EVENT_HANDLERS_FOR_INJECTION, EXTERNAL_EVENT_HANDLERS_FOR_INJECTION, \
    COMMAND_HANDLERS_FOR_INJECTION
from src.organizations.organizations.application.commands import CreateOrganizationRequest
from src.organizations.organizations.infrastructure.rabbitmq.broker import OrganizationRabbitMQBroker

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)

@router.post("/request")
async def create_organization_request(
    #change on Auth domain call
    user: Annotated[ProfileSchema, Depends(get_profile)],
    organization_request: CreateOrganizationRequestSchema
):
    messagebus = MessageBus(
        event_handlers=DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION,
        command_handlers=COMMAND_HANDLERS_FOR_INJECTION,
        broker=OrganizationRabbitMQBroker()
    )
    data = dict(**organization_request.model_dump())
    data["owner_id"] = user.id
    command = CreateOrganizationRequest(**data)
    await messagebus.handle(command)
    return messagebus.command_result