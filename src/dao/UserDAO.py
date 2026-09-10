from sqlalchemy import func, select  # noqa: N999
from sqlalchemy.ext.asyncio import AsyncSession

from db.enums import RoleEnum
from db.models import User
from schemas.authSchema import UserRegister
from schemas.userSchema import FreelancerFilter, UserUpdate


class UserDAO:
    model = User

    @classmethod
    async def create(cls, user_data: UserRegister, session: AsyncSession):
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.password,
            role=user_data.role,
            full_name=user_data.full_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def get_by_id(cls, user_id: int, session: AsyncSession):
        query = select(cls.model).where(cls.model.id == user_id)
        return await session.scalar(query)

    @classmethod
    async def get_by_email(cls, email: str, session: AsyncSession):
        query = select(cls.model).where(cls.model.email == email)
        return await session.scalar(query)

    @classmethod
    async def get_by_username(cls, username: str, session: AsyncSession):
        query = select(cls.model).where(cls.model.username == username)
        return await session.scalar(query)

    @classmethod
    async def update(cls, user_id: int, user_data: UserUpdate, session: AsyncSession):
        query = select(cls.model).where(cls.model.id == user_id)
        user = await session.scalar(query)

        if user is None:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def delete(cls, user_id: int, session: AsyncSession):
        query = select(cls.model).where(
            cls.model.id == user_id,
            cls.model.is_active == True,
        )
        user = await session.scalar(query)

        if user is None:
            return None

        user.is_active = False
        await session.commit()
        return True

    @classmethod
    async def block(cls, user_id: int, session: AsyncSession):
        query = select(cls.model).where(
            cls.model.id == user_id,
            cls.model.is_active == True,
        )
        user = await session.scalar(query)

        if user is None:
            return None

        user.is_active = False
        await session.commit()
        return True

    @classmethod
    async def unblock(cls, user_id: int, session: AsyncSession):
        query = select(cls.model).where(
            cls.model.id == user_id,
            cls.model.is_active == False,
        )
        user = await session.scalar(query)

        if user is None:
            return None

        user.is_active = True
        await session.commit()
        return True

    @classmethod
    async def list(
        cls,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        role: RoleEnum | None = None,
        is_active: bool | None = None,
    ):
        query = select(cls.model)

        if role is not None:
            query = query.where(cls.model.role == role)
        if is_active is not None:
            query = query.where(cls.model.is_active == is_active)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await session.execute(query)
        users = result.scalars().all()

        count_query = select(func.count()).select_from(cls.model)
        if role is not None:
            count_query = count_query.where(cls.model.role == role)
        if is_active is not None:
            count_query = count_query.where(cls.model.is_active == is_active)

        total = await session.scalar(count_query)

        return users, total

    @classmethod
    async def get_freelancers(cls, session: AsyncSession, data=FreelancerFilter):
        query = select(cls.model).where(cls.model.role == RoleEnum.FREELANCER)

        if data.min_rating is not None:
            query = query.where(cls.model.rating >= data.min_rating)

        if data.max_rating is not None:
            query = query.where(cls.model.rating <= data.max_rating)

        if data.skills:
            conditions = []
            for skill in data.skills:
                conditions.append(cls.model.skills.any(func.lower(skill)))
            query = query.where(func.or_(*conditions))

        offset = (data.page - 1) * data.page_size
        query = query.offset(offset).limit(data.page_size)

        result = await session.execute(query)
        users = result.scalars().all()

        count_query = select(func.count()).where(cls.model.role == RoleEnum.FREELANCER)
        if data.min_rating is not None:
            count_query = count_query.where(cls.model.rating >= data.min_rating)
        if data.max_rating is not None:
            count_query = count_query.where(cls.model.rating <= data.max_rating)
        if data.skills:
            conditions = []
            for skill in data.skills:
                conditions.append(cls.model.skills.any(func.lower(skill)))
            count_query = count_query.where(func.or_(*conditions))

        total = await session.scalar(count_query)

        return users, total

    @classmethod
    async def search_by_skills(
        cls,
        session: AsyncSession,
        skills: list[str],
        page: int = 1,
        page_size: int = 20,
    ):
        return await cls.get_freelancers(
            skills=skills,  # type: ignore
            page=page,  # type: ignore
            page_size=page_size,  # type: ignore
            session=session,
        )

    @classmethod
    async def update_rating(cls, session: AsyncSession, user_id: int) -> None:
        from dao.ReviewDAO import ReviewDAO

        stats = await ReviewDAO.get_stats_by_user(session=session, user_id=user_id)
        average_rating = stats.get("average_rating", 0.0)

        query = select(cls.model).where(cls.model.id == user_id)
        user = await session.scalar(query)
        if user:
            user.rating = average_rating
            await session.commit()

    @classmethod
    async def increment_completed_projects(cls, session: AsyncSession, user_id: int):
        user = await cls.get_by_id(session=session, user_id=user_id)
        if user is None:
            return None
        user.compeleted_projects += 1
        await session.commit()
        await session.refresh(user)
        return user
