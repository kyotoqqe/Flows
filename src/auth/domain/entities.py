from dataclasses import dataclass

@dataclass
class User:
    email:str
    username:str
    password:str
    active: bool = False
    #permission stuff

    """ @classmethod
    def create(
        cls, 
        email:str,
        username:str,
        password:str
    ):
        pass """
    
    @classmethod
    def activate(cls):
        cls.active = True

