from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import core_settings


class SpotifyOauthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=core_settings.env_path)

    spotify_oauth_client_id: str = ""
    spotify_oauth_client_secret: str = ""
    spotify_oauth_callback: str = ""


class GoogleOauthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=core_settings.env_path)

    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_callback: str = ""


spotify_oauth_settings = SpotifyOauthSettings()
google_oauth_settings = GoogleOauthSettings()
