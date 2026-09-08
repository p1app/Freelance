from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from db.enums import ContractStatusEnum
from schemas.milestoneSchema import MilestoneResponse
from schemas.reviewSchema import ReviewResponse


class ContractResponse(BaseModel):
    id: int
    project_id: int
    customer_id: int
    freelancer_id: int
    final_price: int
    start_date: datetime
    end_date: datetime | None
    status: ContractStatusEnum

    model_config = ConfigDict(from_attributes=True)


class ContractCreate(BaseModel):
    proposal_id: int
    project_id: int
    customer_id: int
    freelancer_id: int
    final_price: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_users_different(self) -> ContractCreate:
        if self.customer_id == self.freelancer_id:
            raise ValueError("customer_id и freelancer_id должны быть разными")
        return self


class ContractDetailResponse(ContractResponse):
    project_title: str
    customer_name: str
    freelancer_name: str
    milestones: list[MilestoneResponse] | None
    reviews: list[ReviewResponse] | None

    model_config = ConfigDict(from_attributes=True)
