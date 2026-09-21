from typing import Annotated, Literal

from core.database import get_db
from core.security import get_current_user
from fastapi import APIRouter, Depends, status
from models.user_model import User as UserModel
from schemas.notification_schema import NotificationResponse
from service.notification_service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["notification"])


@router.get(
    path="/users/me/notifications",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_list_by_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> list[NotificationResponse]:
    return await NotificationService.get_list_by_user(db, current_user)


@router.patch(
    path="/notifications/{id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def read_by_id(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> NotificationResponse:
    return await NotificationService.read_by_id(db, id, current_user)


@router.patch(
    path="/users/me/notifications",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
async def read_all_by_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> list[NotificationResponse]:
    return await NotificationService.read_all_by_user(db, current_user)


@router.delete(
    path="/notifications/{id}",
    status_code=status.HTTP_200_OK,
)
async def delete_by_id(
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> Literal[True]:
    return await NotificationService.delete_by_id(db, id, current_user)


@router.delete(
    path="/users/me/notifications",
    status_code=status.HTTP_200_OK,
)
async def delete_all_by_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> Literal[True]:
    return await NotificationService.delete_all_by_user(db, current_user)
