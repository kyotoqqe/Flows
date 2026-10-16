from shared.infrastructure.exceptions import InfrastructureException


class StorageException(InfrastructureException):
    pass


class StorageDataInvalidError(StorageException):
    pass


class StorageConcurrencyError(StorageException):
    pass
