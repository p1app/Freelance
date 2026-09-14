from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from models.userModel import User as UserModel
from schemas.milestoneSchema import (
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
)
from schemas.paginationSchema import PaginatedResponse
from service.milestoneService import MilestonService as MilestoneService

router = APIRouter(tags=["milestones"])


@router.get(
    path="/contracts/{contract_id}/milestones",
    response_model=PaginatedResponse[MilestoneResponse],
    status_code=status.HTTP_200_OK,
)
async def get_milestones_by_contract(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[MilestoneResponse]:
    return await MilestoneService.get_milestones_by_contract(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
        page=page,
        page_size=page_size,
    )


@router.post(
    path="/contracts/{contract_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_milestone(
    contract_id: int,
    data: MilestoneCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MilestoneResponse:
    return await MilestoneService.create_milestone(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
        milestone_data=data,
    )


@router.get(
    path="/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def get_milestone(
    milestone_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MilestoneResponse:
    return await MilestoneService.get_milestone(
        session=db,
        current_user=current_user,
        milestone_id=milestone_id,
    )


@router.put(
    path="/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def update_milestone(
    milestone_id: int,
    data: MilestoneUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MilestoneResponse:
    return await MilestoneService.update_milestone(
        session=db,
        current_user=current_user,
        milestone_id=milestone_id,
        data=data,
    )


@router.delete(
    path="/milestones/{milestone_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
async def delete_milestone(
    milestone_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> bool:
    return await MilestoneService.delete_milestone(
        session=db,
        current_user=current_user,
        milestone_id=milestone_id,
    )


@router.patch(
    path="/milestones/{milestone_id}/complete",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def complete_milestone(
    milestone_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MilestoneResponse:
    return await MilestoneService.complete_milestone(
        session=db,
        current_user=current_user,
        milestone_id=milestone_id,
    )


@router.patch(
    path="/milestones/{milestone_id}/approve",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def approve_milestone(
    milestone_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MilestoneResponse:
    return await MilestoneService.approve_milestone(
        session=db,
        current_user=current_user,
        milestone_id=milestone_id,
    )
