from abc import ABC, abstractmethod

from src.auth.application.dto import OauthUserCredentials


class AbstractStateManager(ABC):
    async def set_state(self) -> str:
        raise NotImplementedError

    async def check_state(self, state: str) -> bool:
        raise NotImplementedError


class AbstractOauthClient(ABC):
    def __init__(self, state_manager: AbstractStateManager) -> None:
        self.state_manager = state_manager

    @abstractmethod
    async def generate_oauth_link(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_user_credentials(self, code: str, state: str) -> OauthUserCredentials:
        raise NotImplementedError
