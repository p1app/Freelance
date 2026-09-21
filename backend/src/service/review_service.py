from core.enums import ContractStatusEnum, NotificationTypeEnum
from core.exceptions import BusinessError, ConflictError, ForbiddenError, NotFoundError
from models import User as UserModel
from repository.contract_repo import ContractRepository
from repository.review_repo import ReviewRepository
from repository.user_repo import UserRepository
from schemas.notification_schema import NotificationCreateReview
from schemas.pagination_schema import PaginatedResponse
from schemas.review_schema import (
    ReviewCreate,
    ReviewResponse,
    ReviewStatsResponse,
)
from service.notification_service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession


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
        contract = await ContractRepository.get_by_id(
            session=session, contract_id=contract_id
        )
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
        existing_review = await ReviewRepository.get_by_contract_and_user(
            session=session,
            contract_id=contract_id,
            from_user_id=current_user.id,
        )
        if existing_review:
            raise ConflictError("You have already left a review for this contract")

        # 7. Создание отзыва
        review = await ReviewRepository.create(
            session=session,
            review_data=data,
            contract_id=contract_id,
            from_user_id=current_user.id,
            to_user_id=to_user_id,
        )

        # 8. Обновление рейтинга получателя
        await UserRepository.update_rating(session=session, user_id=to_user_id)

        await NotificationService.create_for_review(
            session=session,
            data=NotificationCreateReview(
                type=NotificationTypeEnum.REVIEW,
                from_user_id=current_user.id,
                to_user_id=to_user_id,
                description="Вам был добавлен новый отзыв",
            ),
        )

        return ReviewResponse.model_validate(review)

    @classmethod
    async def get_review(cls, session: AsyncSession, review_id: int) -> ReviewResponse:
        review = await ReviewRepository.get_by_id(session=session, review_id=review_id)
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
        user = await UserRepository.get_by_id(session=session, user_id=user_id)
        if user is None:
            raise NotFoundError("User not found")

        reviews, total = await ReviewRepository.list_by_user(
            session=session,
            user_id=user_id,
            sort_by_worse=sort_by_worse,
            min_rating=min_rating,
            max_rating=max_rating,
            page=page,
            page_size=page_size,
        )

        validate_data = [ReviewResponse.model_validate(review) for review in reviews]

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
        contract = await ContractRepository.get_by_id(
            session=session, contract_id=contract_id
        )
        if contract is None:
            raise NotFoundError("Contract not found")

        if (
            current_user.id != contract.customer_id
            and current_user.id != contract.freelancer_id
        ):
            raise ForbiddenError("Only contract participants can view reviews")

        reviews = await ReviewRepository.get_by_contract(
            session=session, contract_id=contract_id
        )
        return [ReviewResponse.model_validate(review) for review in reviews]

    @classmethod
    async def get_review_stats(
        cls,
        session: AsyncSession,
        user_id: int,
    ) -> ReviewStatsResponse:
        user = await UserRepository.get_by_id(session=session, user_id=user_id)
        if user is None:
            raise NotFoundError("User not found")

        stats = await ReviewRepository.get_stats_by_user(
            session=session, user_id=user_id
        )
        return ReviewStatsResponse(**stats)
