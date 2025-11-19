from abc import ABC, abstractmethod


class AbstractPaymentProvider(ABC):
    
    @abstractmethod
    def create_checkout(self):
        pass

    @abstractmethod
    def get_payment_info(self):
        pass