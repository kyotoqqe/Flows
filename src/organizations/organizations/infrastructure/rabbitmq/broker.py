from src.core.rabbitmq.message_broker import RabbitMQMessageBroker


from src.organizations import DOMAIN_EVENT_HANDLERS_FOR_INJECTION, EXTERNAL_EVENT_HANDLERS_FOR_INJECTION, \
    COMMAND_HANDLERS_FOR_INJECTION

#create interface
class OrganizationRabbitMQBroker(RabbitMQMessageBroker):
    queue = "organization"
    exchange = "organization"
    event_handlers = DOMAIN_EVENT_HANDLERS_FOR_INJECTION | EXTERNAL_EVENT_HANDLERS_FOR_INJECTION
    command_handlers = COMMAND_HANDLERS_FOR_INJECTION
    router_keys_for_queues = {
        "organization":[
            "organization.request.created",
            "check.organization.existence"
        ]
    }
    
    