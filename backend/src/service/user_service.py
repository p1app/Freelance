from typing import Literal

from core.exceptions import NotFoundError
from models.user_model import User
from repository.project_repo import ProjectRepository
from repository.review_repo import ReviewRepository
from repository.user_repo import UserRepository
from schemas.pagination_schema import PaginatedResponse
from schemas.user_schema import (
    FreelancerFilter,
    UserProfileResponse,
    UserPublicResponse,
    UserStatsResponse,
    UserUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @classmethod
    async def get_profile(cls, current_user: User) -> UserProfileResponse:
        return UserProfileResponse.model_validate(current_user)

    @classmethod
    async def get_public_profile(
        cls, session: AsyncSession, user_id: int
    ) -> UserPublicResponse:
        user_orm = await UserRepository.get_by_id(session=session, user_id=user_id)
        if user_orm is None:
            raise NotFoundError("User not found")
        return UserPublicResponse.model_validate(user_orm)

    @classmethod
    async def delete(
        cls, current_user: User, session: AsyncSession
    ) -> None | Literal[True]:
        return await UserRepository.delete(session=session, user_id=current_user.id)

    @classmethod
    async def update_profile(
        cls,
        session: AsyncSession,
        current_user: User,
        update_data: UserUpdate,
    ) -> UserProfileResponse:
        updated_user = await UserRepository.update(
            session=session,
            user_id=current_user.id,
            user_data=update_data,
        )
        if updated_user is None:
            raise NotFoundError("User not found")
        return UserProfileResponse.model_validate(updated_user)

    @classmethod
    async def get_stats(
        cls, session: AsyncSession, current_user: User
    ) -> UserStatsResponse:
        _, total_projects = await ProjectRepository.get_by_customer(
            session=session,
            customer_id=current_user.id,
        )

        total_completed_projects = await UserRepository.get_completed_projects(
            session=session,
            user_id=current_user.id,
        )

        reviews = await ReviewRepository.get_stats_by_user(
            session=session,
            user_id=current_user.id,
        )

        count_reviews = reviews.get("total_reviews", 0)
        average_rating = reviews.get("average_rating", 0.0)

        return UserStatsResponse(
            projects_count=total_projects,  # type: ignore
            completed_count=total_completed_projects,  # type: ignore
            reviews_count=count_reviews,
            average_rating=average_rating,
        )

    @classmethod
    async def get_freelancers(
        cls,
        session: AsyncSession,
        filters: FreelancerFilter,
    ) -> PaginatedResponse[UserPublicResponse]:
        freelancers, total = await UserRepository.get_freelancers(
            session=session,
            data=filters,  # type: ignore
        )

        valid_freelancers = [
            UserPublicResponse.model_validate(freelancer) for freelancer in freelancers
        ]

        return PaginatedResponse(
            items=valid_freelancers,
            total=total,  # type: ignore
            page=filters.page,
            page_size=filters.page_size,
            pages=(total + filters.page_size - 1) // filters.page_size,  # type: ignore
        )
