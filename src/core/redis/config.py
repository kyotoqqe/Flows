from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import core_settings

class RedisSettings(BaseSettings):
    redis_port: int
    redis_host: str
    redis_password: str

    model_config = SettingsConfigDict(env_file=core_settings.base_dir / ".env", extra="ignore")

redis_settings = RedisSettings()