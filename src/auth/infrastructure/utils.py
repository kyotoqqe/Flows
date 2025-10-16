import json

from passlib.context import CryptContext
from base64 import urlsafe_b64encode, urlsafe_b64decode
from dataclasses import asdict

from fastapi import Request
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict

from src.config import core_settings

from src.auth.domain.dto  import Base64TokenPayload
from src.auth.config import cookie_settings

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    bcrypt__rounds = 12,
    deprecated = "auto"
)

def generated_password_hash(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(input_password:str, password_hash:str) -> bool:
    return pwd_context.verify(input_password, password_hash)

def generate_token(user_id: int):
    payload = Base64TokenPayload(user_id = user_id)
    payload_as_dict = asdict(payload)
    payload_as_json = json.dumps(payload_as_dict)
    token_encode = urlsafe_b64encode(payload_as_json.encode()) 
    return token_encode.decode()

def decode_token(token: str) -> Base64TokenPayload:

    payload = urlsafe_b64decode(token)
    payload_json = json.loads(payload.decode())
    payload_model = Base64TokenPayload(**payload_json)

    if datetime.now(timezone.utc) > datetime.fromisoformat(payload_model.exp):
        #raise invalid token send confirm email again
        print("invalid confirm token")
        
        pass

    return payload_model.user_id

def create_confirmation_link(token: str) -> str:
    return  f"{core_settings.base_url}api/auth/confirm/?token={token}"

def create_password_reset_link(token: str) -> str:
    return f"{core_settings.base_url}api/auth/password/reset/confirm/?token={token}"

#move to oauth maybe
class OAuth2Cookie(OAuth2):
    
    def __init__(self,  *, 
                 token_url: str, 
                 scheme_name: Optional[str] = None, 
                 scopes: Optional[Dict[str, str]] = None,
                 description: Optional[str] = None, 
                 auto_error: bool = True
        ):
        
        if not scopes:
            scopes = {}
        
        flows = OAuthFlows(password = {"tokenUrl": token_url, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error
        )
        
    async def __call__(self, request: Request) -> Optional[str]:
        token = request.cookies.get(cookie_settings.cookie_key)

        if not token:
            if self.auto_error:
                raise #NotAuthenticatedError
            return None
        return token

oauth2_scheme_cookie = OAuth2Cookie(token_url="auth/login")