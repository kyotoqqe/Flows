from src.core.rabbitmq.message_broker import RabbitMQMessageBroker

<<<<<<< Updated upstream
from src.organizations import EVENT_HANDLERS_FOR_INJECTION, COMMAND_HANDLERS_FOR_INJECTION
=======
from src.organizations import DOMAIN_EVENT_HANDLERS_FOR_INJECTION, EXTERNAL_EVENT_HANDLERS_FOR_INJECTION, \
    COMMAND_HANDLERS_FOR_INJECTION
>>>>>>> Stashed changes

#create interface
class OrganizationRabbitMQBroker(RabbitMQMessageBroker):
    queue = "organization"
    exchange = "organization"
<<<<<<< Updated upstream
    event_handlers = EVENT_HANDLERS_FOR_INJECTION
=======
    event_handlers = DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION
>>>>>>> Stashed changes
    command_handlers = COMMAND_HANDLERS_FOR_INJECTION
    router_keys_for_queues = {
        "organization":[
            "organization.request.created",
            "check.organization.existence"
        ]
    }
    
    