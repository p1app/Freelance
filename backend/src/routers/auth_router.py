from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_jwt_harmony import JWTHarmony, JWTHarmonyDep, JWTHarmonyRefresh
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.exceptions import ConflictError
from core.security import JWTUser
from schemas.auth_schema import TokenResponse, UserLogin, UserRegister
from service.auth_service import AuthService

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


@router.post("/logout")
async def logout(authorize: Annotated[JWTHarmony[JWTUser], Depends(JWTHarmonyDep)]):
    try:
        await AuthService.logout(authorize.get_raw_jwt())
        return {"message": "Вы успешно вышли из системы"}
    except:  # noqa: E722
        raise ConflictError("Conflict in logout")
