from sqlalchemy import select, func

from db.models import Review
from db.database import async_session_maker
from schemas.review import ReviewCreate, ReviewUpdate


class ReviewDAO:
    model = Review

    @classmethod
    async def create(cls, review_data: ReviewCreate, contract_id: int, from_user_id: int, to_user_id: int):
        async with async_session_maker() as session:
            review = Review(
                **review_data.model_dump(),
                contract_id=contract_id,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )
            session.add(review)
            await session.commit()
            await session.refresh(review)
            return review

    @classmethod
    async def get_by_id(cls, review_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == review_id)
            return await session.scalar(query)

    @classmethod
    async def update(cls, review_id: int, review_data: ReviewUpdate):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == review_id)
            review = await session.scalar(query)

            if review is None:
                return None

            update_data = review_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(review, key, value)

            await session.commit()
            await session.refresh(review)
            return review

    @classmethod
    async def delete(cls, review_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == review_id)
            review = await session.scalar(query)

            if review is None:
                return None

            await session.delete(review)
            await session.commit()
            return True

    @classmethod
    async def list_by_user(
        cls,
        user_id: int,
        min_rating: float | None = None,
        max_rating: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.to_user_id == user_id)

            if min_rating:
                query = query.where(cls.model.rating >= min_rating)
            if max_rating:
                query = query.where(cls.model.rating <= max_rating)

            count_query = select(func.count()).where(cls.model.to_user_id == user_id)
            if min_rating:
                count_query = count_query.where(cls.model.rating >= min_rating)
            if max_rating:
                count_query = count_query.where(cls.model.rating <= max_rating)

            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            reviews = result.scalars().all()

            return reviews, total

    @classmethod
    async def get_stats_by_user(cls, user_id: int):
        async with async_session_maker() as session:
            # Общее количество
            count_query = select(func.count()).where(cls.model.to_user_id == user_id)
            total = await session.scalar(count_query)

            # Средний рейтинг
            avg_query = select(func.avg(cls.model.rating)).where(cls.model.to_user_id == user_id)
            avg_rating = await session.scalar(avg_query)

            # Распределение по рейтингу
            dist_query = (
                select(cls.model.rating, func.count())
                .where(cls.model.to_user_id == user_id)
                .group_by(cls.model.rating)
            )
            result = await session.execute(dist_query)
            distribution = {int(rating): count for rating, count in result}

            return {
                "total_reviews": total,
                "average_rating": avg_rating or 0.0,
                "rating_distribution": distribution,
            }

    @classmethod
    async def get_by_contract(cls, contract_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.contract_id == contract_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_average_rating(cls, user_id: int) -> float:
        async with async_session_maker() as session:
            query = select(func.avg(cls.model.rating)).where(cls.model.to_user_id == user_id)
            avg = await session.scalar(query)
            return avg or 0.0