class InfrastructureException(Exception):
    _message = "Infrastructure exception"

    def __init__(self, *args):
        super().__init__(self._message)