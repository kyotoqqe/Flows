from src.organizations.organizations.application.units_of_work import RedisOrganizationRequestsUnitOfWork, \
        SQLAlchemyOrganizationsUnitOfWork
from src.organizations.organizations.domain.events import OrganizationCreated
from src.organizations.organizations.application.commands import CreateOrganizationRequest, CheckOrganizationExistence, \
        DeleteOrganizationRequest
from src.organizations.organizations.application.handlers import CreateOrganizationHandler, CreateOrganizationRequestHandler, \
        CheckOrganizationExistenceHandler, DeleteOrganizationRequestHandler

from src.organizations.membership.application.handlers import CreateMembershipHandler
from src.organizations.membership.application.units_of_work import SQLAlchemyMembershipsUnitOfWork

#change this
from src.payments.application.events import OrganizationPaymentSucceeded



DOMAIN_EVENT_HANDLERS_FOR_INJECTION = {
    OrganizationCreated: [
        CreateMembershipHandler(uow=SQLAlchemyMembershipsUnitOfWork())
    ],
}

EXTERNAL_EVENT_HANDLERS_FOR_INJECTION = {
    
}

EVENT_HANDLERS_FOR_INJECTION = {
    #maybe create separate dict for external events
    OrganizationPaymentSucceeded: [
        CreateOrganizationHandler(uow=SQLAlchemyOrganizationsUnitOfWork())
    ]
}

COMMAND_HANDLERS_FOR_INJECTION = {
    CreateOrganizationRequest: [
        CreateOrganizationRequestHandler(uow=RedisOrganizationRequestsUnitOfWork(), ttl = 15 * 60)
    ],
    CheckOrganizationExistence: [
        CheckOrganizationExistenceHandler(uow=SQLAlchemyOrganizationsUnitOfWork())
    ],
    DeleteOrganizationRequest: [
        DeleteOrganizationRequestHandler(uow=RedisOrganizationRequestsUnitOfWork())
    ],
}
