from typing import Annotated, Literal

from core.database import get_db
from core.security import get_current_user
from fastapi import APIRouter, Depends, status
from models.user_model import User as UserModel
from schemas.pagination_schema import PaginatedResponse
from schemas.user_schema import (
    FreelancerFilter,
    UserProfileResponse,
    UserPublicResponse,
    UserStatsResponse,
    UserUpdate,
)
from service.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    path="/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK
)
async def get_me(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserProfileResponse:
    return await UserService.get_profile(current_user)


@router.put(
    path="/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK
)
async def put_update_me(
    update_data: UserUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserProfileResponse:
    return await UserService.update_profile(db, current_user, update_data)


@router.get(
    path="/me/stats",
    response_model=UserStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_me_stats(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserStatsResponse:
    return await UserService.get_stats(db, current_user)


@router.get(
    path="/freelancers",
    response_model=PaginatedResponse[UserPublicResponse],
    status_code=status.HTTP_200_OK,
)
async def get_freelancers(
    filters: Annotated[FreelancerFilter, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaginatedResponse[UserPublicResponse]:
    return await UserService.get_freelancers(db, filters)


@router.get(
    path="/{user_id}", response_model=UserPublicResponse, status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublicResponse:
    return await UserService.get_public_profile(db, user_id)


@router.delete(path="/me", response_model=bool, status_code=status.HTTP_200_OK)
async def delete_me(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None | Literal[True]:
    return await UserService.delete(current_user, db)
