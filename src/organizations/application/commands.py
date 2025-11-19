from dataclasses import dataclass

from src.core.interfaces.commands import Command

@dataclass
class CreateOrganizationRequest(Command):
    name: str
    nickname: str
    owner_id: int

@dataclass
class CheckOrganizationExistence(Command):
    nickname: str

@dataclass
class DeleteOrganizationRequest(Command):
    name: str
    nickname: str