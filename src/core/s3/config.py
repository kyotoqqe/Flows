from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import core_settings

class S3Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str

    model_config = SettingsConfigDict(env_file=core_settings.base_dir / ".env", extra="ignore")

s3_settings = S3Settings()

