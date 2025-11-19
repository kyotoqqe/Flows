from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import core_settings

class StripeSettings(BaseSettings):
    success_url: str
    cancel_url: str
    api_key: str
    endpoint_secret: str

    model_config = SettingsConfigDict(env_file=core_settings.base_dir / ".env", env_prefix="STRIPE_", extra="ignore")

stripe_settings = StripeSettings()