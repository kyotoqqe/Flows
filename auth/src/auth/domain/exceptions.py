from shared.domain.exceptions import DomainException


class WeakPassword(DomainException):
    pass


class InvalidEmailError(DomainException):
    pass


class RefreshSessionLimitExceeded(DomainException):
    pass


class RefreshSessionIsExpired(DomainException):
    pass


class RefreshSessionNotFound(DomainException):
    pass


class OauthProviderException(DomainException):
    pass


class UserBanException(DomainException):
    pass
