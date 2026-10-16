import base64
from uuid import uuid4

from src.auth.application.dto import OauthUserCredentials
from src.auth.application.exceptions import InvalidOauthState
from src.auth.application.external.oauth import AbstractOauthClient, AbstractStateManager
from src.auth.domain.value_objs import Provider


class FakeStateManager(AbstractStateManager):
    def __init__(self) -> None:
        self.storage = set()

    async def set_state(self) -> str:
        rand_str = str(uuid4())
        state = base64.b64encode(rand_str.encode()).decode()
        self.storage.add(state)
        return state

    async def check_state(self, state: str) -> bool:
        return state in self.storage


class FakeOauthClient(AbstractOauthClient):
    async def generate_oauth_link(self) -> str:
        state = await self.state_manager.set_state()
        return f"https://fake-oauth-provider?state={state}"

    async def get_user_credentials(self, code: str, state: str) -> OauthUserCredentials:
        if not await self.state_manager.check_state(state):
            raise InvalidOauthState("The states do not match")
        return OauthUserCredentials(
            email="test.email@gmail.com",
            provider_user_id="822de25d-8e0b-46be-866e-e5b0279eb71f",
            provider=Provider.GOOGLE,
        )
