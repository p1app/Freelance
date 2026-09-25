from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.enums import RoleEnum


class UserRegisterNoPass(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    role: RoleEnum
    fullname: str = Field(min_length=2, max_length=60)


class UserRegister(UserRegisterNoPass):
    password: str = Field(min_length=6, max_length=50)


class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    fullname: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=50)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class ErrorResponse(BaseModel):
    detail: str
    status_code: int
