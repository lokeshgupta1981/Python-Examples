from pydantic import BaseModel, Field


class ProductCopy(BaseModel):
    title: str = Field(max_length=60)
    description: str = Field(max_length=600)
    bullets: list[str] = Field(min_length=3, max_length=5)
    meta_title: str = Field(max_length=60)
    meta_description: str = Field(max_length=155)
    used_attributes: list[str]
