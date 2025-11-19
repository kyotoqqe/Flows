from src.organizations.organizations.application.units_of_work import RedisOrganizationRequestsUnitOfWork, \
        SQLAlchemyOrganizationsUnitOfWork
from src.organizations.organizations.application.commands import CreateOrganizationRequest, CheckOrganizationExistence, \
        DeleteOrganizationRequest
from src.organizations.organizations.application.handlers import CreateOrganizationHandler, CreateOrganizationRequestHandler, \
        CheckOrganizationExistenceHandler, DeleteOrganizationRequestHandler

from src.payments.application.events import OrganizationPaymentSucceeded


DOMAIN_EVENT_HANDLERS_FOR_INJECTION = {

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
    ]
}
