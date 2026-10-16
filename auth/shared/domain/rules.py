class BaseRule:
    __message = "Business rule is broken"

    def get_message(self):
        return self.__message

    def is_broken(self) -> bool:
        raise NotImplementedError
