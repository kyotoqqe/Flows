from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

from src.config import core_settings

class CelerySettings(BaseSettings):
    task_serializer: str
    result_serializer: str
    accept_content: list[str]
    broker_url: str
    result_backend: str
    #worker_prefech_multiplier: int

    model_config = SettingsConfigDict(
        env_prefix="CELERY_",
        env_file=core_settings.base_dir / ".env", 
        extra="ignore"
    )

@lru_cache
def get_celery_settings():
    return CelerySettings()
celery_settings = CelerySettings()