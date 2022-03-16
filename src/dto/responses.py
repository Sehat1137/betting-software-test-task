from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    key: str


class GetBodyResponse(BaseModel):
    body: dict
    duplicates: int


class AddBodyResponse(BaseResponse):
    ...


class UpdateBodyResponse(BaseResponse):
    ...


class GetStatsResponse(BaseModel):
    duplicates: float = Field(description="percentage of duplicates")
