from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import core_settings
from sqlalchemy import URL


class PostgresDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=core_settings.env_path, extra="ignore")

    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    postgres_driver: str = "asyncpg"

    @property
    def get_db_url(self):
        url = URL.create(
            host=self.postgres_host,
            port=self.postgres_port,
            username=self.postgres_user,
            password=self.postgres_password,
            database=self.postgres_db,
            drivername=f"postgresql+{self.postgres_driver}",
        )

        return url.render_as_string(hide_password=False)


postgres_db_settings = PostgresDBSettings()
