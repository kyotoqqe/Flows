from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


from src.auth.application.ports.tokens import TokenProvider
from src.auth.infrastructure.security.config import jwt_settings


class JWTTokenProvider(TokenProvider):
    def encode(self, payload: dict) -> str:
        expired_at = datetime.now(tz=timezone.utc) + timedelta(minutes=5)
        payload["expired_at"] = expired_at
        token = jwt.encode(
            payload, jwt_settings.jwt_rsa_private_key, algorithm=jwt_settings.jwt_algorithm
        )
        return token

    def decode(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token, jwt_settings.jwt_rsa_public_key, algorithms=[jwt_settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise
