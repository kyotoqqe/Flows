import asyncio
from abc import ABC, abstractmethod

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher


class AbstractPasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, raw_password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, raw_password: str, password_hash: str) -> bool:
        raise NotImplementedError

    async def async_hash_password(self, raw_password: str) -> str:
        return await asyncio.to_thread(self.hash_password, raw_password)

    async def async_verify_password(self, raw_password: str, password_hash: str) -> bool:
        return await asyncio.to_thread(self.verify_password, raw_password, password_hash)


class BcryptPasswordHasher(AbstractPasswordHasher):
    hasher = PasswordHash([BcryptHasher()])

    def hash_password(self, raw_password: str) -> str:
        return self.hasher.hash(raw_password)

    def verify_password(self, raw_password: str, password_hash: str) -> bool:
        return self.hasher.verify(raw_password, password_hash)
