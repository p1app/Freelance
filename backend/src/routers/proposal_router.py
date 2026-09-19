from typing import Annotated

from core.database import get_db
from core.enums import ProposalStatusEnum
from core.security import get_current_client, get_current_freelancer
from fastapi import APIRouter, Depends, Query, status
from models.user_model import User as UserModel
from schemas.contract_schema import ContractResponse
from schemas.pagination_schema import PaginatedResponse
from schemas.proposal_schema import (
    ProposalCreate,
    ProposalResponse,
    ProposalUpdate,
)
from service.proposal_service import ProposalService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["proposals"])


@router.get(
    path="/proposals/me",
    response_model=PaginatedResponse[ProposalResponse],
    status_code=status.HTTP_200_OK,
)
async def get_proposals_by_freelancer(
    current_user: Annotated[UserModel, Depends(get_current_freelancer)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: Annotated[ProposalStatusEnum | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ProposalResponse]:
    return await ProposalService.get_my_proposals(
        session=db,
        current_user=current_user,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    path="/proposals/me/{project_id}",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
)
async def get_proposal_by_freelancer_by_project(
    current_user: Annotated[UserModel, Depends(get_current_freelancer)],
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: int,
) -> ProposalResponse:
    return await ProposalService.get_my_proposal_by_project(
        session=db,
        current_user=current_user,
        project_id=project_id,
    )


@router.get(
    path="/projects/{project_id}/proposals",
    response_model=PaginatedResponse[ProposalResponse],
    status_code=status.HTTP_200_OK,
)
async def get_proposals_by_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
    status_filter: Annotated[ProposalStatusEnum | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ProposalResponse]:
    return await ProposalService.get_proposals_by_project(
        session=db,
        current_user=current_user,
        project_id=project_id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.post(
    path="/projects/{project_id}/proposals",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_proposal(
    project_id: int,
    data: ProposalCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_freelancer)],
) -> ProposalResponse:
    return await ProposalService.create_proposal(
        session=db,
        data=data,
        project_id=project_id,
        freelancer_id=current_user.id,
    )


@router.put(
    path="/proposals/{proposal_id}",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
)
async def update_proposal(
    proposal_id: int,
    data: ProposalUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_freelancer)],
) -> ProposalResponse:
    return await ProposalService.update_proposal(
        session=db,
        current_user=current_user,
        proposal_id=proposal_id,
        data=data,
    )


@router.delete(
    path="/proposals/{proposal_id}",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
)
async def withdraw_proposal(
    proposal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_freelancer)],
) -> ProposalResponse:
    return await ProposalService.withdraw_proposal(
        session=db,
        current_user=current_user,
        proposal_id=proposal_id,
    )


@router.patch(
    path="/proposals/{proposal_id}/accept",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
async def accept_proposal(
    proposal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> ContractResponse:
    return await ProposalService.accept_proposal(
        session=db,
        current_user=current_user,
        proposal_id=proposal_id,
    )


@router.patch(
    path="/proposals/{proposal_id}/reject",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
)
async def reject_proposal(
    proposal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_client)],
) -> ProposalResponse:
    return await ProposalService.reject_proposal(
        session=db,
        current_user=current_user,
        proposal_id=proposal_id,
    )
