from shared.domain.aggregates import Aggregate


class AppilcationException(Exception):
    pass


class EntityNotFound(AppilcationException):
    def __init__(self, entity: type[Aggregate], **kwargs):
        message = f"{entity} entity with {kwargs} not found"
        super().__init__(message)
        self.entity = entity
        self.kwargs = kwargs


class EntityAlreadyExist(AppilcationException):
    def __init__(self, entity: type[Aggregate], **kwargs):
        message = f"{entity} entity with {kwargs} already exist"
        super().__init__(message)
        self.entity = entity
        self.kwargs = kwargs


class MappedEventMismatchException(AppilcationException):
    pass


class IntegrationEventAlreadyRegistrated(AppilcationException):
    pass


class HandlerMappingError(AppilcationException):
    pass


class CommandAlreadyRegistrated(AppilcationException):
    pass


class HandlerNotFound(AppilcationException):
    pass
