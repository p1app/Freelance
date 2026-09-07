from datetime import datetime

from db.enums import ProjectStatusEnum, RoleEnum
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class AdminProjectResponse(BaseModel):
    id: int
    title: str
    status: ProjectStatusEnum
    budget: int
    customer_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PlatformStatsResponse(BaseModel):
    total_users: int
    clients_count: int
    freelancers_count: int
    total_projects: int
    in_progress_projects: int
    completed_projects: int
    total_contracts: int
    active_contracts: int
    average_rating: float = Field(default=0.0)

    model_config = ConfigDict(from_attributes=True)