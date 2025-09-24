from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class CoreSettings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent
    base_url: HttpUrl

    #media_path: str = "/media/"
    #media_url: str = base_url + media_path

    model_config = SettingsConfigDict(env_file=f"{base_dir}/.env", extra="ignore")

core_settings = CoreSettings()