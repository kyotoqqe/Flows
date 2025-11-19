import inspect
from typing import Dict, Callable, Union, Any

from src.core.interfaces.events import AbstractEvent
from src.core.interfaces.commands import Command
from src.core.interfaces.message_broker import MessageBroker

class MessageBus:
    
    def __init__(self,
        event_handlers: Dict[AbstractEvent, Callable],
        command_handlers: Dict[Command, Callable],
        broker:MessageBroker 
        ):
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.broker = broker
        self._command_result: Any = None
    
    def _get_event_or_command_from_dict(self, data: Dict):
        try:
            event_type = data.pop("type")
            for event in self.event_handlers.keys():
                event_name = event.__name__
                if event_type == event_name:
                    return event(**data)
                
            for command in self.command_handlers.keys():
                command_name = command.__name__
                print(command_name)
                if event_type == command_name:
                    return command_name
            
            raise ValueError("Event or command not found")
        except KeyError:
            raise ValueError("Incorrect data")
        
    async def handle(self, message: Union[AbstractEvent, Command], **kwargs):
        print(type(message))
        if isinstance(message, dict):
            message = self._get_event_or_command_from_dict(message)
        if isinstance(message, AbstractEvent):
            await self._handle_event(message)
        elif isinstance(message, Command):
            await self._handle_command(message, **kwargs)
        else: 
            raise TypeError("Message type must be Event or Command") #maybe create custom error

    async def _handle_event(self, event: AbstractEvent):
        #test 
        try:
            key = self.event_handlers[type(event)]
        except KeyError:
            return await self.broker.publish(event)
        for handler in key:
            if "messagebus" in inspect.signature(handler).parameters:
                await handler(event, self)
            else:
                await handler(event)
                                    
            for event in handler.uow.events:
                self.broker.publish(event)

    async def _handle_command(self, command: Command, **kwargs):
         for handler in self.command_handlers[type(command)]:
            if "messagebus" in inspect.signature(handler).parameters:
                self._command_result = await handler(command, self, **kwargs)
            else:
                self._command_result = await handler(command, **kwargs)
                                    
            for event in handler.uow.events:
                await self.broker.publish(event)

    @property
    def command_result(self):
        return self._command_result