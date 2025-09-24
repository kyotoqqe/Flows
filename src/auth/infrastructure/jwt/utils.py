import jwt
from jwt.exceptions import  InvalidTokenError ,ExpiredSignatureError 

from src.auth.schemas import JWTTokenPayload
from src.auth.infrastructure.jwt.config import jwt_settings

def create_jwt_token(payload: JWTTokenPayload):
    payload = payload.model_dump()
    
    access_token = jwt.encode(
        payload=payload,
        key=jwt_settings.jwt_secret,
        algorithm=jwt_settings.algorithm
    ) 

    return access_token

def decode_jwt_token(token: str) -> JWTTokenPayload:
    try:
        print(token)
        data = jwt.decode(
            jwt=token,
            key=jwt_settings.jwt_secret,
            algorithms=jwt_settings.algorithm
        )
        return JWTTokenPayload(
            user_id = data["user_id"],
            exp = data["exp"]
        )
    except (ExpiredSignatureError, InvalidTokenError):
        raise