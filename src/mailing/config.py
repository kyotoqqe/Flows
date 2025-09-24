from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import core_settings

class EmailSettings(BaseSettings):
    email_sender: str
    email_passcode: str
    smtp_host: str
    smtp_port: int

    model_config = SettingsConfigDict(env_file=core_settings.base_dir / ".env", extra="ignore") 

email_settings = EmailSettings()