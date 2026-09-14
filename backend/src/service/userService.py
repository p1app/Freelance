from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError
from models.userModel import User
from repository.projectRepo import ProjectRepository
from repository.reviewRepo import ReviewRepository
from repository.userRepo import UserRepository
from schemas.paginationSchema import PaginatedResponse
from schemas.userSchema import (
    FreelancerFilter,
    UserProfileResponse,
    UserPublicResponse,
    UserStatsResponse,
    UserUpdate,
)


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

        _, total_projects_freelance = await ProjectRepository.get_by_freelancer(
            session=session,
            freelancer_id=current_user.id,
        )

        reviews = await ReviewRepository.get_stats_by_user(
            session=session,
            user_id=current_user.id,
        )

        count_reviews = reviews.get("total_reviews", 0)
        average_rating = reviews.get("average_rating", 0.0)

        return UserStatsResponse(
            projects_count=total_projects,  # type: ignore
            completed_count=total_projects_freelance,  # type: ignore
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
