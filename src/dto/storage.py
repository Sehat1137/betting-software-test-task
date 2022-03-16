from pydantic import BaseModel


class BodyEntry(BaseModel):
    body: dict
    duplicates: int
