from src.core.domain.exceptions import BusinessRuleException
class BaseRule:
    
    __message: str = "Business rule is broken"
    exception = BusinessRuleException

    def get_message(self) -> str:
        return self.__message
    
    def is_broken(self) -> bool:
        pass

    def __str__(self):
        return "This is a base rule"
    

