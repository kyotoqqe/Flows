from dataclasses import dataclass

from shared.application.events.events import IntegrationEvent


@dataclass(frozen=True, kw_only=True)
class UserActivationRequested(IntegrationEvent):
    email: str
    activation_token: str
