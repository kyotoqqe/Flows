import base64

from urllib import parse
from aiohttp import FormData
from shared.infrastructure.ipc.rpc.exceptions import RpcClientError
from src.auth.application.dto import OauthUserCredentials
from src.auth.application.external.oauth import AbstractOauthClient
from src.auth.domain.value_objs import Provider
from src.auth.infrastructure.external.oauth.config import spotify_oauth_settings
from shared.infrastructure.ipc.rpc.adapters.http.client import HttpRpcCLient


class SpotifyOauthClient(AbstractOauthClient):
    def __init__(self) -> None:
        self.base_url = "https://accounts.spotify.com/"
        self.client_id = spotify_oauth_settings.spotify_oauth_client_id
        self.client_secret = spotify_oauth_settings.spotify_oauth_client_secret
        self.redirect_uri = spotify_oauth_settings.spotify_oauth_callback

    def generate_oauth_link(self) -> str:
        query_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": " ".join(
                [
                    "user-read-private",
                    "user-read-email",
                ]
            ),
            "redirect_uri": self.redirect_uri,
            "show_dialog": True,
        }

        query_string = parse.urlencode(query_params, quote_via=parse.quote)
        return self.base_url + "authorize?" + query_string

    async def get_user_credential(
        self, code: str, state: str | None = None
    ) -> OauthUserCredentials:
        form = FormData()
        form.add_field("code", code)
        form.add_field("redirect_uri", self.redirect_uri)
        form.add_field("grant_type", "authorization_code")

        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "
            + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode(),
        }

        rpc = HttpRpcCLient(base_url=self.base_url)
        try:
            res = await rpc.call("POST", endpoint="api/token", headers=headers, form_data=form)
            access_token = res["access_token"]
            rpc.base_url = "https://api.spotify.com/"
            user = await rpc.call(
                "GET", endpoint="v1/me", headers={"Authorization": f"Bearer {access_token}"}
            )
            return OauthUserCredentials(
                email=user["email"], provider_user_id=user["account_id"], provider=Provider.SPOTIFY
            )
        except RpcClientError as e:
            raise
