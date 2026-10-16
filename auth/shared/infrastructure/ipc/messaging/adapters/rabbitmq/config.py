from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import core_settings


class RabbitMQSettings(BaseSettings):
    rabbitmq_default_user: str = "guest"
    rabbitmq_default_pass: str = "guest"
    rabbitmq_default_host: str = "rabbitmq"

    model_config = SettingsConfigDict(env_file=core_settings.env_path, extra="ignore")


rabbitmq_settings = RabbitMQSettings()
