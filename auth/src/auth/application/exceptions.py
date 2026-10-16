from shared.application.exceptions import AppilcationException


class PasswordsMismatchException(AppilcationException):
    pass


class ActivationTimeExpired(AppilcationException):
    pass


class InvalidOauthState(AppilcationException):
    pass
