import json
from abc import ABC, abstractmethod
from base64 import urlsafe_b64encode
from hashlib import sha256

from cryptography.fernet import Fernet

from src.auth.infrastructure.security.config import secrets_settings


class AbstractTokenGenerator(ABC):
    @abstractmethod
    def encrypt(self, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, token: str) -> dict:
        raise NotImplementedError


class FernetTokenGenerator(AbstractTokenGenerator):
    def __init__(self) -> None:
        key_bytes = secrets_settings.fernet_secret_key.encode("utf-8")
        key_digest = sha256(key_bytes).digest()
        key_base64 = urlsafe_b64encode(key_digest)
        self._fernet = Fernet(key_base64)

    def encrypt(self, payload: dict) -> str:
        payload_json = json.dumps(payload)
        return self._fernet.encrypt(payload_json.encode("utf-8")).decode("utf-8")

    def decrypt(self, token: str) -> dict:
        payload_json = self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        return json.loads(payload_json)
