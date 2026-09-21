from typing import Annotated

from core.database import get_db
from core.security import get_current_user
from fastapi import APIRouter, Depends, Query, status
from models.user_model import User as UserModel
from schemas.chat_schema import (
    MessageCreate,  # noqa: F401
    MessageResponse,
    UnreadCountResponse,  # noqa: F401
)
from schemas.pagination_schema import PaginatedResponse
from service.chat_service import ChatService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["chat"])


@router.get(
    path="/contracts/{contract_id}/messages",
    response_model=PaginatedResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
)
async def get_messages(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[MessageResponse]:
    return await ChatService.get_messages(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
        page=page,
        page_size=page_size,
    )


# @router.post(
#     path="/contracts/{contract_id}/messages",
#     response_model=MessageResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# async def send_message(
#     contract_id: int,
#     data: MessageCreate,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     current_user: Annotated[UserModel, Depends(get_current_user)],
# ) -> MessageResponse:
#     return await ChatService.send_message(
#         session=db,
#         current_user=current_user,
#         contract_id=contract_id,
#         data=data,
#     )


# @router.patch(
#     path="/messages/{message_id}/read",
#     response_model=bool,
#     status_code=status.HTTP_200_OK,
# )
# async def mark_as_read(
#     message_id: int,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     current_user: Annotated[UserModel, Depends(get_current_user)],
# ) -> bool:
#     return await ChatService.mark_as_read(
#         session=db,
#         current_user=current_user,
#         message_id=message_id,
#     )


# @router.patch(
#     path="/contracts/{contract_id}/messages/read-all",
#     response_model=bool,
#     status_code=status.HTTP_200_OK,
# )
# async def mark_all_as_read(
#     contract_id: int,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     current_user: Annotated[UserModel, Depends(get_current_user)],
# ) -> bool:
#     return await ChatService.mark_all_as_read(
#         session=db,
#         current_user=current_user,
#         contract_id=contract_id,
#     )


# @router.get(
#     path="/contracts/{contract_id}/messages/unread",
#     response_model=UnreadCountResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def get_unread_count(
#     contract_id: int,
#     db: Annotated[AsyncSession, Depends(get_db)],
#     current_user: Annotated[UserModel, Depends(get_current_user)],
# ) -> UnreadCountResponse:
#     return await ChatService.get_unread_count(
#         session=db,
#         current_user=current_user,
#         contract_id=contract_id,
#     )
