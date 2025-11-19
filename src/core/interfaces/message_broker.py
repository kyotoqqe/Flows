from abc import ABC

class MessageBroker(ABC):
    queue = None

    async def publish(self):
        pass

    async def receive(self):
        pass