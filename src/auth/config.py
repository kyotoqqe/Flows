from pydantic_settings import BaseSettings, SettingsConfigDict

from src.auth.infrastructure.jwt.config import jwt_settings
from src.config import core_settings

from typing import Optional

class CookieSettings(BaseSettings):
    cookie_key: str
    cookie_secure: bool
    max_age: int = 60 * 60 * 24 * jwt_settings.refresh_token_expire_days
    cookie_samesite: str
    cookie_domain: Optional[str ]=None
    cookie_path: str
    cookie_httponly: bool

    model_config = SettingsConfigDict(env_file= core_settings.base_dir / ".env", extra="ignore")

cookie_settings = CookieSettings()

#add passlib settings