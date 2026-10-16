from abc import ABC, abstractmethod


class AbstractAccessTokenProvider(ABC):
    @abstractmethod
    def encode(self, payload: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode(self, token: str) -> dict:
        raise NotImplementedError


class AbstractAcessTokenBanlist(ABC):
    pass
