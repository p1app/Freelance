from datetime import datetime

from pydantic import ConfigDict, Field, BaseModel, EmailStr
from db.enums import RoleEnum

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6)
    role: RoleEnum
    full_name: str = Field(min_length=2, max_length=60)

class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    full_name: str 
    created_at: datetime

    model_config=ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")

class RefreshRequest(BaseModel):
    refresh_token: str

class ErrorResponse(BaseModel):
    detail: str
    status_code: int