from src.core.rabbitmq.message_broker import RabbitMQMessageBroker

class PaymentsRabbitMQBroker(RabbitMQMessageBroker):
    queue = "payments"
    exchange = "payments"
    event_handlers = {}
    command_handlers = {}
    router_keys_for_queues = {
       "payments": [],
       "organization": [
           "organization.payment.succeeded"
       ]
    }