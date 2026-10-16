from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from shared.config import core_settings


class TestPostgresDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=core_settings.env_path, extra="ignore")

    test_postgres_host: str = ""
    test_postgres_port: int = 5432
    test_postgres_user: str = ""
    test_postgres_password: str = ""
    test_postgres_db: str = ""
    test_postgres_driver: str = "asyncpg"

    @property
    def get_db_url(self):
        url = URL.create(
            host=self.test_postgres_host,
            port=self.test_postgres_port,
            username=self.test_postgres_user,
            password=self.test_postgres_password,
            database=self.test_postgres_db,
            drivername=f"postgresql+{self.test_postgres_driver}",
        )

        return url.render_as_string(hide_password=False)


test_postgres_db_settings = TestPostgresDBSettings()
