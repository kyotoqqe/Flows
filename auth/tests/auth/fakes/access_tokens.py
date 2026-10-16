import json
import base64


from src.auth.application.ports.tokens import AbstractAccessTokenProvider


class FakeAccessTokenProvider(AbstractAccessTokenProvider):
    def encode(self, payload: dict) -> str:
        json_bytes = json.dumps(payload).encode("utf-8")
        return base64.b64encode(json_bytes).decode("ascii")

    def decode(self, token: str) -> dict:
        decoded_bytes = base64.b64decode(token)
        return json.loads(decoded_bytes.decode("utf-8"))
