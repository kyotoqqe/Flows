from fastapi import Form, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError

class Checker:
    def __init__(self, pydantic_model: BaseModel):
        self.pydantic_model = pydantic_model

    def __call__(self, data: str = Form(...)):
        try:
            return self.pydantic_model.model_validate_json(data)
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=jsonable_encoder(e.errors())
            )