import base64
import json

from src.auth.infrastructure.security.tokens import AbstractTokenGenerator


class FakeTokenGenerator(AbstractTokenGenerator):
    def encrypt(self, payload: dict) -> str:
        json_bytes = json.dumps(payload).encode("utf-8")
        return base64.b64encode(json_bytes).decode("ascii")

    def decrypt(self, token: str) -> dict:
        decoded_bytes = base64.b64decode(token)
        return json.loads(decoded_bytes.decode("utf-8"))
