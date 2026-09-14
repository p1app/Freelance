from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_admin
from core.enums import ProjectStatusEnum, RoleEnum
from models.userModel import User as UserModel
from schemas.adminSchema import (
    AdminProjectResponse,
    AdminUserResponse,
    PlatformStatsResponse,
)
from schemas.paginationSchema import PaginatedResponse
from service.adminService import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    path="/users",
    response_model=PaginatedResponse[AdminUserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
    role: Annotated[RoleEnum | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[AdminUserResponse]:
    return await AdminService.get_all_users(
        current_user=current_user,
        session=db,
        role=role,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )


@router.get(
    path="/users/{user_id}",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
) -> AdminUserResponse:
    return await AdminService.get_user(
        current_user=current_user,
        session=db,
        user_id=user_id,
    )


@router.patch(
    path="/users/{user_id}/block",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
async def block_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
) -> bool:
    return await AdminService.block_user(
        session=db,
        current_user=current_user,
        user_id=user_id,
    )


@router.patch(
    path="/users/{user_id}/unblock",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
async def unblock_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
) -> bool:
    return await AdminService.unblock_user(
        session=db,
        current_user=current_user,
        user_id=user_id,
    )


@router.get(
    path="/projects",
    response_model=PaginatedResponse[AdminProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
    status_filter: Annotated[ProjectStatusEnum | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[AdminProjectResponse]:
    return await AdminService.get_all_projects(
        current_user=current_user,
        session=db,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.delete(
    path="/projects/{project_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
async def delete_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
) -> bool:
    return await AdminService.delete_project(
        current_user=current_user,
        project_id=project_id,
        session=db,
    )


@router.get(
    path="/stats",
    response_model=PlatformStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin)],
) -> PlatformStatsResponse:
    return await AdminService.get_stats(
        session=db,
        current_user=current_user,
    )
