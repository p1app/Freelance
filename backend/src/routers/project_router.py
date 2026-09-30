from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import (
    get_current_client,
    get_current_freelancer,
    get_current_user_optional,
)
from models.user_model import User as UserModel
from schemas.pagination_schema import PaginatedResponse
from schemas.project_schema import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListFilter,
    ProjectResponse,
    ProjectUpdate,
)
from service.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    path="",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def list_projects(
    filters: Annotated[ProjectListFilter, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaginatedResponse[ProjectResponse]:
    return await ProjectService.list_open_projects(db, filters)


@router.get(
    path="/me",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def get_my_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ProjectResponse]:
    return await ProjectService.get_my_projects(db, current_user, page, page_size)


@router.get(
    path="/me/working",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
async def get_working_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_freelancer)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ProjectResponse]:
    return await ProjectService.get_working_projects(db, current_user, page, page_size)


@router.get(
    path="/{project_id}",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel | None, Depends(get_current_user_optional)],
) -> ProjectDetailResponse:
    return await ProjectService.get_project(db, project_id, current_user)


@router.post(
    path="",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project_data: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> ProjectResponse:
    return await ProjectService.create_project(db, project_data, current_user.id)


@router.put(
    path="/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> ProjectResponse:
    return await ProjectService.update_project(
        db, project_id, project_data, current_user
    )


@router.delete(
    path="/{project_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> Literal[True]:
    return await ProjectService.delete_project(db, current_user, project_id)


@router.patch(
    path="/{project_id}/publish",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def publish_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> ProjectResponse:
    return await ProjectService.publish_project(db, current_user, project_id)


@router.patch(
    path="/{project_id}/cancel",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> ProjectResponse:
    return await ProjectService.cancel_project(db, current_user, project_id)
