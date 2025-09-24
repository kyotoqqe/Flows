from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import core_settings

class JWTSettings(BaseSettings):
    jwt_secret: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    algorithm: str

    model_config = SettingsConfigDict(
        env_file=core_settings.base_dir / ".env",
        extra="ignore"
    )

jwt_settings = JWTSettings()