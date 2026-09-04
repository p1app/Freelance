from datetime import datetime

from db.enums import MilestoneStatusEnum
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=5, max_length=50)
    description: str = Field(min_length=5, max_length=5000)
    due_date: datetime

    @model_validator(mode="after")
    def validate_due_date(self) -> "MilestoneCreate":
        if self.due_date < datetime.now():
            raise ValueError(
                f"Время в поле due_date не должно быть раньше настоящего времени"
            )
        return self

class MilestoneUpdate(BaseModel):
    title: str | None = Field(min_length=5, max_length=50)
    description: str | None = Field(min_length=5, max_length=5000)
    due_date: datetime | None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "MilestoneUpdate":
        data = self.model_dump(exclude_unset=True)
        if all(value is None for value in data.values()):
            raise ValueError("Хотя бы одно поле должно быть передано")
        return self

    @model_validator(mode="after")
    def validate_due_date(self) -> "MilestoneUpdate":
        if self.due_date is not None and self.due_date < datetime.now():
            raise ValueError(
                f"Время в поле due_date не должно быть раньше настоящего времени"
            )
        return self

class MilestoneResponse(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    status: MilestoneStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)