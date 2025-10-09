
class BaseRule:
    
    __message: str = "Business rule is broken"

    def get_message(self) -> str:
        return self.__message
    
    def is_broken(self) -> bool:
        pass
    

