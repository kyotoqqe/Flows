from abc import ABC

class AbstractEmailSender(ABC):
    content = None

    def send_email(self):
        pass