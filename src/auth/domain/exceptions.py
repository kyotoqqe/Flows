from src.core.domain.exceptions import DomainException

class RefreshSessionLimitExceededException(DomainException):
    _message = "You can't have more sessions than five."

    def __init__(self, *args):
        super().__init__(self._message)
