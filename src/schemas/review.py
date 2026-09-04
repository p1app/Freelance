from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReviewCreate(BaseModel):
    rating: float = Field(ge=1.0, le=5.0)
    comment: str | None = Field(default=None, max_length=250)


class ReviewUpdate(BaseModel):
    rating: float | None = Field(default=None, ge=1.0, le=5.0)
    comment: str | None = Field(default=None, max_length=250)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ReviewUpdate":
        data = self.model_dump(exclude_unset=True)
        if all(value is None for value in data.values()):
            raise ValueError("Хотя бы одно поле должно быть передано")
        return self


class ReviewResponse(BaseModel):
    id: int
    from_user_id: int
    from_user_name: str
    to_user_id: int
    to_user_name: str
    rating: float
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewStatsResponse(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: dict[int, int] 

    model_config = ConfigDict(from_attributes=True)