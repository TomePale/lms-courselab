from pydantic import BaseModel, Field, field_validator

from app.schemas.common import reject_null


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Programiranje"])


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)

    _not_null = field_validator("name", mode="before")(reject_null)


class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
