from src.auth.infrastructure.security.hasher import AbstractPasswordHasher


class FakePasswordHasher(AbstractPasswordHasher):
    def hash_password(self, raw_password: str) -> str:
        return raw_password

    def verify_password(self, raw_password: str, password_hash: str) -> bool:
        return raw_password == password_hash
