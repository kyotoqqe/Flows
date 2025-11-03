from src.core.exceptions import InfrastructureException

class PasswordDontMatchException(InfrastructureException):
    _message = "The passwords don't match"

class ActivationTokenExpiredError(InfrastructureException):
    _message = "The activation token has expired."
