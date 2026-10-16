from dataclasses import dataclass

from shared.application.commands import Command


@dataclass(frozen=True, kw_only=True)
class CreateUser(Command):
    username: str
    email: str
