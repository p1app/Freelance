from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from models.userModel import User as UserModel
from schemas.paginationSchema import PaginatedResponse
from schemas.reviewSchema import (
    ReviewCreate,
    ReviewResponse,
    ReviewStatsResponse,
    ReviewUpdate,
)
from service.reviewService import ReviewService

router = APIRouter(tags=["reviews"])


@router.post(
    path="/contracts/{contract_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    contract_id: int,
    data: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> ReviewResponse:
    return await ReviewService.create_review(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
        data=data,
    )


@router.get(
    path="/contracts/{contract_id}/reviews",
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_contract(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> list[ReviewResponse]:
    return await ReviewService.get_reviews_by_contract(
        session=db,
        current_user=current_user,
        contract_id=contract_id,
    )


@router.get(
    path="/users/{user_id}/reviews",
    response_model=PaginatedResponse[ReviewResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    min_rating: Annotated[int | None, Query(ge=1, le=5)] = None,
    max_rating: Annotated[int | None, Query(ge=1, le=5)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    sort_by_worse: Annotated[bool, Query()] = False,
) -> PaginatedResponse[ReviewResponse]:
    return await ReviewService.get_reviews_by_user(
        session=db,
        user_id=user_id,
        min_rating=min_rating,
        max_rating=max_rating,
        page=page,
        page_size=page_size,
        sort_by_worse=sort_by_worse,
    )


@router.get(
    path="/users/{user_id}/reviews/stats",
    response_model=ReviewStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_review_stats(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewStatsResponse:
    return await ReviewService.get_review_stats(
        session=db,
        user_id=user_id,
    )


@router.put(
    path="/reviews/{review_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> ReviewResponse:
    return await ReviewService.update_review(
        session=db,
        current_user=current_user,
        review_id=review_id,
        data=data,
    )


@router.delete(
    path="/reviews/{review_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
)
async def delete_review(
    review_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> bool:
    return await ReviewService.delete_review(
        session=db,
        current_user=current_user,
        review_id=review_id,
    )
