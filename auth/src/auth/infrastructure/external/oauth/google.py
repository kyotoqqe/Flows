import jwt
from urllib import parse
from shared.infrastructure.ipc.rpc.adapters.http.client import HttpRpcCLient
from shared.infrastructure.ipc.rpc.exceptions import RpcClientError
from src.auth.application.dto import OauthUserCredentials
from src.auth.domain.value_objs import Provider
from src.auth.infrastructure.external.oauth.config import google_oauth_settings


from src.auth.application.external.oauth import AbstractOauthClient


class GoogleOauthClient(AbstractOauthClient):
    def __init__(self) -> None:
        self.base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.client_id = google_oauth_settings.google_oauth_client_id
        self.redirect_uri = google_oauth_settings.google_oauth_callback
        self.client_secret = google_oauth_settings.google_oauth_client_secret

    def generate_oauth_link(self) -> str:
        query_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(["openid", "profile", "email"]),
        }

        query_string = parse.urlencode(query_params, quote_via=parse.quote)
        return self.base_url + "?" + query_string

    async def get_user_credential(
        self, code: str, state: str | None = None
    ) -> OauthUserCredentials:

        rpc = HttpRpcCLient("https://oauth2.googleapis.com/")
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }
            data = await rpc.call("POST", "token", json_data=data)
            user_data = jwt.decode(
                data["id_token"], algorithms=["RS256"], options={"verify_signature": False}
            )
            return OauthUserCredentials(
                email=user_data["email"],
                provider_user_id=user_data["sub"],
                provider=Provider.GOOGLE,
            )
        except RpcClientError as e:
            raise
