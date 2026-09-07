from pydantic import BaseModel, Field, ConfigDict
from typing import TypeVar, Generic

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0, description="Общее количество записей")
    page: int = Field(ge=1, description="Текущая страница")
    page_size: int = Field(ge=1, le=100, description="Количество записей на странице")
    pages: int = Field(ge=0, description="Общее количество страниц")

    model_config = ConfigDict(from_attributes=True)