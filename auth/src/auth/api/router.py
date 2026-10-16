from fastapi import APIRouter

from src.auth.infrastructure.external.oauth.google import GoogleOauthClient
from src.auth.infrastructure.external.oauth.spotify import SpotifyOauthClient


router = APIRouter(prefix="/auth", tags=["Authentification & Authorization"])


@router.get("/login/spotify")
def get_spotify_oauth_uri():
    oauth = SpotifyOauthClient()
    return oauth.generate_oauth_link()


@router.post("/spotify/callback")
async def spotify_oauth_login(
    code: str,
):
    oauth = SpotifyOauthClient()
    return await oauth.get_user_credential(code=code)


@router.get("/login/google")
def get_google_oauth_uri():
    oauth = GoogleOauthClient()
    return oauth.generate_oauth_link()


@router.post("/google/callback")
async def google_oauth_login(
    code: str,
):
    oauth = GoogleOauthClient()
    return await oauth.get_user_credential(code=code)
