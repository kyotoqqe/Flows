from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_path: Path = Path(__file__).parent

    @computed_field
    @property
    def env_path(self) -> Path:
        return self.base_path / ".env"


core_settings = CoreSettings()
