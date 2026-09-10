from operator import attrgetter
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessError, ConflictError, ForbiddenError, NotFoundError
from dao.ConractDAO import ContractDAO
from dao.ReviewDAO import ReviewDAO
from dao.UserDAO import UserDAO
from db.enums import ContractStatusEnum
from db.models import User as UserModel
from schemas.paginationSchema import PaginatedResponse
from schemas.reviewSchema import (
    ReviewCreate,
    ReviewResponse,
    ReviewStatsResponse,
    ReviewUpdate,
)


class ReviewService:
    @classmethod
    async def create_review(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
        data: ReviewCreate,
    ) -> ReviewResponse:
        # 1. Проверка, что контракт существует
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")

        # 2. Проверка, что контракт завершён
        if contract.status != ContractStatusEnum.COMPLETED:
            raise BusinessError("Only COMPLETED contracts can be reviewed")

        # 3. Проверка, что пользователь — участник контракта
        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can leave reviews")

        # 4. Определяем, кому ставим отзыв
        if current_user.id == contract.customer_id:
            to_user_id = contract.freelancer_id
        else:
            to_user_id = contract.customer_id

        # 5. Проверка, что пользователь не ставит отзыв самому себе
        if current_user.id == to_user_id:
            raise BusinessError("You cannot leave a review for yourself")

        # 6. Проверка, что отзыв ещё не оставлен
        existing_review = await ReviewDAO.get_by_contract_and_user(
            session=session,
            contract_id=contract_id,
            from_user_id=current_user.id,
        )
        if existing_review:
            raise ConflictError("You have already left a review for this contract")

        # 7. Создание отзыва
        review = await ReviewDAO.create(
            session=session,
            review_data=data,
            contract_id=contract_id,
            from_user_id=current_user.id,
            to_user_id=to_user_id,
        )

        # 8. Обновление рейтинга получателя
        await UserDAO.update_rating(session=session, user_id=to_user_id)

        return ReviewResponse.model_validate(review)

    @classmethod
    async def get_review(cls, session: AsyncSession, review_id: int) -> ReviewResponse:
        review = await ReviewDAO.get_by_id(session=session, review_id=review_id)
        if review is None:
            raise NotFoundError("Review not found")
        return ReviewResponse.model_validate(review)

    @classmethod
    async def get_reviews_by_user(
        cls,
        session: AsyncSession,
        user_id: int,
        min_rating: int | None = None,
        max_rating: int | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by_worse: bool = False,
    ) -> PaginatedResponse[ReviewResponse]:
        user = await UserDAO.get_by_id(session=session, user_id=user_id)
        if user is None:
            raise NotFoundError("User not found")

        reviews, total = await ReviewDAO.list_by_user(
            session=session,
            user_id=user_id,
            min_rating=min_rating,
            max_rating=max_rating,
            page=page,
            page_size=page_size,
        )

        validate_data = [ReviewResponse.model_validate(review) for review in reviews]

        if sort_by_worse:
            validate_data.sort(key=attrgetter("rating"))
        else:
            validate_data.sort(key=attrgetter("rating"), reverse=True)

        return PaginatedResponse(
            items=validate_data,
            total=total,  # type: ignore
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,  # type: ignore
        )

    @classmethod
    async def get_reviews_by_contract(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        contract_id: int,
    ) -> list[ReviewResponse]:
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can view reviews")

        reviews = await ReviewDAO.get_by_contract(
            session=session, contract_id=contract_id
        )
        return [ReviewResponse.model_validate(review) for review in reviews]

    @classmethod
    async def update_review(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        review_id: int,
        data: ReviewUpdate,
    ) -> ReviewResponse:
        review = await ReviewDAO.get_by_id(session=session, review_id=review_id)
        if review is None:
            raise NotFoundError("Review not found")

        if review.from_user_id != current_user.id:
            raise ForbiddenError("You can only update your own review")

        updated_review = await ReviewDAO.update(
            session=session,
            review_id=review_id,
            review_data=data,
        )

        # Пересчёт рейтинга получателя
        await UserDAO.update_rating(session=session, user_id=updated_review.to_user_id)  # type: ignore

        return ReviewResponse.model_validate(updated_review)

    @classmethod
    async def delete_review(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        review_id: int,
    ) -> Literal[True]:
        review = await ReviewDAO.get_by_id(session=session, review_id=review_id)
        if review is None:
            raise NotFoundError("Review not found")

        if review.from_user_id != current_user.id:
            raise ForbiddenError("You can only delete your own review")

        to_user_id = review.to_user_id

        await ReviewDAO.delete(session=session, review_id=review_id)

        # Пересчёт рейтинга получателя
        await UserDAO.update_rating(session=session, user_id=to_user_id)

        return True

    @classmethod
    async def get_review_stats(
        cls,
        session: AsyncSession,
        user_id: int,
    ) -> ReviewStatsResponse:
        user = await UserDAO.get_by_id(session=session, user_id=user_id)
        if user is None:
            raise NotFoundError("User not found")

        stats = await ReviewDAO.get_stats_by_user(session=session, user_id=user_id)
        return ReviewStatsResponse(**stats)
