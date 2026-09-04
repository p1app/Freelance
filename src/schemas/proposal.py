from datetime import datetime

from db.enums import ProposalStatusEnum
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProposalCreate(BaseModel):
    cover_letter: str = Field(min_length=10, max_length=200)
    bid_amount: int = Field(gt=0)
    estimated_days: int

class ProposalUpdate(BaseModel):
    cover_letter: str | None = Field(min_length=10, max_length=200)
    bid_amount: int | None = Field(gt=0)
    estimated_days: int | None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ProposalUpdate":
        data = self.model_dump(exclude_unset=True)
        if all(value is None for value in data.values()):
            raise ValueError("Хотя бы одно поле должно быть передано")
        return self

class ProposalResponse(BaseModel):
    id: int 
    freelancer_id: int
    freelancer_name: str
    cover_letter: str
    bid_amount: int
    estimated_days: int
    status: ProposalStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config=ConfigDict(from_attributes=True)