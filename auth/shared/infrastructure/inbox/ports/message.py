from uuid import UUID


class InboxMessage:
    def __init__(
        self, message_id: UUID, correlation_id: UUID, type: str, handler_name: str, timestamp: int
    ):
        self.message_id = message_id
        self.correlation_id = correlation_id
        self.type = type
        self.handler_name = handler_name
        self.timestamp = timestamp
