from datetime import datetime
from pydantic import ConfigDict, Field, BaseModel, EmailStr, model_validator
from db.enums import ProjectCategoryEnum, ProjectStatusEnum
from schemas.proposal import ProposalResponse

class ProjectCreate(BaseModel):
    title: str = Field(min_length=5, max_length=255)
    description: str = Field(min_length=20, max_length=5000)
    budget: int = Field(gt=0)
    deadline: datetime
    category: ProjectCategoryEnum

    @model_validator(mode="after")
    def validate_deadline(self) -> "ProjectCreate":
        if self.deadline < datetime.now():
            raise ValueError(
                f"Время в поле deadline не должно быть раньше настоящего времени"
            )
        return self

class ProjectUpdate(BaseModel):
    title: str | None = Field(min_length=5, max_length=255)
    description: str | None = Field(min_length=20, max_length=5000)
    budget: int | None = Field(gt=0)
    deadline: datetime | None
    category: ProjectCategoryEnum | None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ProjectUpdate":
        data = self.model_dump(exclude_unset=True)
        if all(value is None for value in data.values()):
            raise ValueError("Хотя бы одно поле должно быть передано")
        return self

    @model_validator(mode="after")
    def validate_deadline(self) -> "ProjectUpdate":
        if self.deadline is not None and self.deadline < datetime.now():
            raise ValueError(
                f"Время в поле deadline не должно быть раньше чем настоящее время"
            )
        return self

class ProjectResponse(BaseModel):
    id: int
    title: str 
    description: str 
    budget: int 
    deadline: datetime 
    category: ProjectCategoryEnum 
    status: ProjectStatusEnum
    customer_id: int
    freelancer_id: int | None
    created_at: datetime

    model_config=ConfigDict(from_attributes=True)

class ProjectDetailResponse(ProjectResponse):
    customer_name: str
    freelancer_name: str | None
    proposal_count: int | None
    proposals: list[ProposalResponse] | None

    @model_validator(mode="after")
    def freelancer_name_validate(self) -> "ProjectDetailResponse":
        if self.freelancer_id is None:
            self.freelancer_name = None
        return self

class ProjectListFilter(BaseModel):
    category: ProjectCategoryEnum | None
    status: ProjectStatusEnum | None
    budget_min: int | None = Field(ge=0)
    budget_max: int | None
    search: str | None
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)

    @model_validator(mode="after")
    def budget_range_validate(self):
        if self.budget_min is not None and self.budget_max is not None:
            if self.budget_max < self.budget_min:
                raise ValueError("budget_max не может быть меньше budget_min")
        return self


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatusEnum