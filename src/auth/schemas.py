from pydantic import BaseModel, EmailStr, field_validator, model_validator, UUID4

from typing import Self

class PaswordMixin(BaseModel):
    password: str
    password2: str

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str):
        rules = {
            "isdigit_rule": False,
            "isupper_rule": False,
            "islower_rule": False,
            "special_symbol_rule": False,
        }

        if len(value) < 8:
            raise ValueError("Password is too weak.\
                          It must be at least 8 characters long and include digits,\
                          uppercase and lowercase letters, and at least one special symbol.")

        for ch in value:
            if not rules["isdigit_rule"] and ch.isdigit():
                rules["isdigit_rule"] = True
            elif not rules["isupper_rule"] and ch.isupper():
                rules["isupper_rule"] = True
            elif not rules["islower_rule"] and ch.islower():
                rules["islower_rule"] = True
            elif not rules["special_symbol_rule"] and ch in "!@#$%^&*()-_=+[]{};:,.<>?/\\|":
                rules["special_symbol_rule"] = True 

        if all(rule for rule in rules.values()):
            return value
        
        raise ValueError("Password is too weak.\
                          It must be at least 8 characters long and include digits,\
                          uppercase and lowercase letters, and at least one special symbol.") #WeakPassword
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password2:
            raise ValueError('Passwords do not match') #PasswordMatchError
        return self
class RegistrationSchema(PaswordMixin):
    email: EmailStr
    username: str
    

class UserSchema(BaseModel):
    id: int
    email: str
    active: bool

class LoginSchema(BaseModel):
    email: str
    password: str

class PasswordResetSchema(PaswordMixin):
    token: str
