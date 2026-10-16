from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import core_settings


class SecretsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=core_settings.env_path, extra="ignore")

    fernet_secret_key: str = ""


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=core_settings.env_path, extra="ignore")

    jwt_rsa_private_key: str = ""
    jwt_rsa_public_key: str = ""
    jwt_algorithm: str = "RS256"


secrets_settings = SecretsSettings()
jwt_settings = JWTSettings()
