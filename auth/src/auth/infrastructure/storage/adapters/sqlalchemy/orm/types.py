import uuid

from sqlalchemy import UUID, Dialect, String, TypeDecorator

from src.auth.domain.value_objs import Email, Password, UserId


class UserIdDB(TypeDecorator[UserId]):
    impl = UUID

    cache_ok = True

    def process_bind_param(self, value: UserId | None, dialect: Dialect) -> uuid.UUID | None:
        if value is not None and hasattr(value, "value"):
            return value.value

    def process_result_value(self, value: uuid.UUID | None, dialect: Dialect) -> UserId | None:
        if value is not None:
            return UserId(value=value)


class EmailDB(TypeDecorator[Email]):
    impl = String

    cache_ok = True

    def process_bind_param(self, value: Email | None, dialect: Dialect) -> str | None:
        if value is not None and hasattr(value, "value"):
            return value.value

    def process_result_value(self, value: str | None, dialect: Dialect) -> Email | None:
        if value is not None:
            return Email(value=value)


class PasswordDB(TypeDecorator[Password]):
    impl = String

    cache_ok = True

    def process_bind_param(self, value: Password | None, dialect: Dialect) -> str | None:
        if value is not None and hasattr(value, "value"):
            return value.value

    def process_result_value(self, value: str | None, dialect: Dialect) -> Password | None:
        if value is not None:
            return Password(value=value)
