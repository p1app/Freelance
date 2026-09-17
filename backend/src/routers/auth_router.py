from typing import Annotated

from core.database import get_db
from core.security import JWTUser, get_current_user
from fastapi import APIRouter, Depends, status
from fastapi_jwt_harmony import JWTHarmony, JWTHarmonyRefresh
from models.user_model import User as UserModel
from schemas.auth_schema import TokenResponse, UserLogin, UserRegister
from service.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post(
    path="/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await AuthService.register(user_data=data, session=db)


@router.post(
    path="/login", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def login(
    data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await AuthService.login(session=db, login_data=data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    Authorize: Annotated[JWTHarmony[JWTUser], Depends(JWTHarmonyRefresh)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await AuthService.refresh(db, Authorize.user_claims)


@router.post(path="/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    return await AuthService.logout(current_user)
