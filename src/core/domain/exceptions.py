from src.core.interfaces.model import AbstractModel

class DomainException(Exception):
    pass

class BusinessRuleException(DomainException):
    pass

#maybe move to infra
class EntityNotFound(Exception):
    def __init__(self, model: AbstractModel, **kwargs):
        message = f"{model} entity with {kwargs} not found"
        super().__init__(message)
        self.model = model
        self.kwargs = kwargs

class EntityAlreadyExist(Exception):
    def __init__(self, model: AbstractModel, **kwargs):
        message = f"{model} entity with {kwargs} already exist"
        super().__init__(message)
        self.model = model
        self.kwargs = kwargs