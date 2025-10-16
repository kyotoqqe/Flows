from src.core.domain.rules import BaseRule

from src.auth.domain.exceptions import RefreshSessionLimitExceededException

class IsValidRefreshSessionCount(BaseRule):
    __message = "Refresh sessions count must be less than {valid_refresh_session_number}"
    VALID_REFRESH_SESSION_NUMBER = 5
    exception = RefreshSessionLimitExceededException

    def __init__(self, sessions_count: int):
        self.count = sessions_count
    
    def is_broken(self) -> bool:
        return self.count > self.VALID_REFRESH_SESSION_NUMBER
    
    def get_message(self) -> str:
        return self.__message.format(valid_refresh_session_number = self.VALID_REFRESH_SESSION_NUMBER)
    
