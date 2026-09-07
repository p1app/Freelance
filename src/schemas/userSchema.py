from datetime import datetime
from pydantic import ConfigDict, Field, BaseModel, EmailStr, model_validator
from db.enums import RoleEnum


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=60)
    bio: str | None = Field(default=None, max_length=500)
    skills: list[str] | None = Field(default=None)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserUpdate":
        data = self.model_dump(exclude_unset=True)
        if all(value is None for value in data.values()):
            raise ValueError("Хотя бы одно поле должно быть передано")
        return self


class UserPublicResponse(BaseModel):
    id: int
    username: str
    full_name: str
    bio: str | None
    skills: list[str] | None
    rating: float
    completed_projects: int

    model_config = ConfigDict(from_attributes=True)


class UserStatsResponse(BaseModel):
    projects_count: int
    completed_count: int
    reviews_count: int
    average_rating: float | None

    model_config = ConfigDict(from_attributes=True)


class FreelancerFilter(BaseModel):
    skills: list[str] | None = None
    min_rating: float | None = Field(default=None, ge=0)
    max_rating: float | None = Field(default=None, le=5)
    search: str | None = Field(default=None, min_length=1)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: RoleEnum
    bio: str | None
    skills: list[str] | None
    rating: float
    completed_projects: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    