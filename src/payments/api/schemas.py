from pydantic import BaseModel
from decimal import Decimal
from typing import Union, Literal

class BaseCheckout(BaseModel):
    price: Decimal
    quantity: int


class OrganizationCheckout(BaseCheckout):
    type: Literal["organization"]
    name: str
    nickname: str
    owner_id: int

Services = Union[OrganizationCheckout]