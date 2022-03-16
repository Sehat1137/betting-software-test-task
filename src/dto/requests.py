from fastapi import Query
from pydantic import BaseModel


class AddBodyParams(BaseModel):
    __root__: dict


class GetBodyParams:
    def __init__(self, key: str = Query(...)):
        self.key: str = key


class BaseParams(BaseModel):
    key: str


class RemoveKeyParams(BaseParams):
    ...


class UpdateBodyParams(BaseParams):
    body: dict
