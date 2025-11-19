from pydantic import BaseModel

class CreateOrganizationRequestSchema(BaseModel):
    name: str
    nickname: str