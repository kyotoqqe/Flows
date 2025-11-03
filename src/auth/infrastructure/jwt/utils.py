import jwt
from jwt.exceptions import  InvalidTokenError ,ExpiredSignatureError 
from dataclasses import asdict

from src.auth.infrastructure.dto import JWTTokenPayload
from src.auth.infrastructure.jwt.config import jwt_settings

def create_jwt_token(payload: JWTTokenPayload):
    payload_as_dict = asdict(payload)
    
    access_token = jwt.encode(
        payload=payload_as_dict,
        key=jwt_settings.jwt_secret,
        algorithm=jwt_settings.algorithm
    ) 

    return access_token

def decode_jwt_token(token: str) -> JWTTokenPayload:
    try:
        data = jwt.decode(
            jwt=token,
            key=jwt_settings.jwt_secret,
            algorithms=jwt_settings.algorithm
        )
        return JWTTokenPayload(
            user_id = data["user_id"],
            exp = data["exp"],
            role = data["role"]
        )
    except (ExpiredSignatureError, InvalidTokenError):
        raise