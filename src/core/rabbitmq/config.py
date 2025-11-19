from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import core_settings


class RabbitMQSettings(BaseSettings):
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    rabbitmq_default_host: str

    model_config = SettingsConfigDict(env_file=core_settings.base_dir / ".env", extra="ignore")

rabbitmq_settings = RabbitMQSettings() 