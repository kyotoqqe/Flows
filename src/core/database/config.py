from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy import URL

ENV_PATH = Path(__file__).parent / ".." / ".." / ".." / ".env"

class DatabaseSettings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_driver: str = "asyncpg"

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def get_db_url(self) -> str:
        url = URL.create(
            drivername=f"postgresql+{self.postgres_driver}",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db
        )

        return url.render_as_string(hide_password=False)

db_settings = DatabaseSettings()