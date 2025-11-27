from fastapi import APIRouter, Depends
from typing import Annotated

from src.core.messagebus import MessageBus

from src.profiles.dependencies import get_profile
from src.profiles.schemas import ProfileSchema

from src.organizations import DOMAIN_EVENT_HANDLERS_FOR_INJECTION, EXTERNAL_EVENT_HANDLERS_FOR_INJECTION, \
    COMMAND_HANDLERS_FOR_INJECTION
from src.organizations.organizations.infrastructure.rabbitmq.broker import OrganizationRabbitMQBroker

from src.organizations.membership.api.schemas import CreateMemberSchema, DeleteMemberSchema, ChangeOwnerSchema, UpdateMemberSchema
from src.organizations.membership.application.commands import CreateMember, DeleteMember, ChangeOwner, UpdateMember

router = APIRouter(
    prefix="/memberships",
    tags=["Memberships"]
)

@router.post("/create_member")
async def create_member(
        profile: Annotated[ProfileSchema, Depends(get_profile)],
        member: CreateMemberSchema
):
    data = member.model_dump()
    data["inviter_id"] = profile.id

    messagebus = MessageBus(
        event_handlers=DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION,
        command_handlers=COMMAND_HANDLERS_FOR_INJECTION,
        broker=OrganizationRabbitMQBroker()
    )
    command = CreateMember(
        **data
    )

    await messagebus.handle(command)
    return messagebus.command_result

@router.delete("/delete_member")
async def delete_member(
    profile: Annotated[ProfileSchema, Depends(get_profile)],
    data: DeleteMemberSchema
):
    data = data.model_dump()
    data["actor_id"] = profile.id

    messagebus = MessageBus(
        event_handlers=DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION,
        command_handlers=COMMAND_HANDLERS_FOR_INJECTION,
        broker=OrganizationRabbitMQBroker()
    )
    command = DeleteMember(
        **data
    )

    await messagebus.handle(command)
    return messagebus.command_result
    
@router.post("change_owner")
async def change_owner(
    profile: Annotated[ProfileSchema, Depends(get_profile)],
    data: ChangeOwnerSchema
):
    data = data.model_dump()
    data["actor_id"] = profile.id

    messagebus = MessageBus(
        event_handlers=DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION,
        command_handlers=COMMAND_HANDLERS_FOR_INJECTION,
        broker=OrganizationRabbitMQBroker()
    )
    command = ChangeOwner(
        **data
    )
    await messagebus.handle(command)
    return messagebus.command_result

@router.put("/update/member")
async def update_member(
    profile: Annotated[ProfileSchema, Depends(get_profile)],
    data: UpdateMemberSchema
):
    update_data = data.model_dump()
    update_data["actor_id"] = profile.id

    messagebus = MessageBus(
        event_handlers=DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION,
        command_handlers=COMMAND_HANDLERS_FOR_INJECTION,
        broker=OrganizationRabbitMQBroker()
    )
    command = UpdateMember(
        **data
    )
    await messagebus.handle(command)
    return messagebus.command_result