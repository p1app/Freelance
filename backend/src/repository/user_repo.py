from core.enums import RoleEnum
from models import User
from schemas.auth_schema import UserRegisterNoPass
from schemas.user_schema import FreelancerFilter, UserUpdate
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    model = User

    @classmethod
    async def create(
        cls, user_data: UserRegisterNoPass, session: AsyncSession, hashed_password: str
    ):
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            fullname=user_data.fullname,
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
    def _skill_condition(cls, skill: str):
        # EXISTS (SELECT 1 FROM unnest(users.skills) AS s WHERE lower(s) = lower(:skill))
        s = func.unnest(cls.model.skills).column_valued("s")
        return select(1).select_from(s).where(func.lower(s) == skill.lower()).exists()

    @classmethod
    async def get_freelancers(cls, session: AsyncSession, data: FreelancerFilter):
        conditions = [cls.model.role == RoleEnum.FREELANCER]

        if data.min_rating is not None:
            conditions.append(cls.model.rating >= data.min_rating)
        if data.max_rating is not None:
            conditions.append(cls.model.rating <= data.max_rating)
        if data.skills:
            conditions.append(or_(*[cls._skill_condition(s) for s in data.skills]))
        if data.search:
            conditions.append(
                or_(
                    cls.model.username.ilike(f"%{data.search}%"),
                    cls.model.fullname.ilike(f"%{data.search}%"),
                )
            )

        total = await session.scalar(
            select(func.count()).select_from(cls.model).where(*conditions)
        )

        query = (
            select(cls.model)
            .where(*conditions)
            .order_by(cls.model.rating.desc(), cls.model.id.desc())
            .offset((data.page - 1) * data.page_size)
            .limit(data.page_size)
        )
        users = (await session.execute(query)).scalars().all()

        return users, total or 0

    @classmethod
    async def update_rating(cls, session: AsyncSession, user_id: int) -> None:
        from repository.review_repo import ReviewRepository

        stats = await ReviewRepository.get_stats_by_user(
            session=session, user_id=user_id
        )
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
        user.completed_projects += 1
        await session.flush()
        await session.refresh(user)
        return user

    @classmethod
    async def get_completed_projects(cls, session: AsyncSession, user_id: int):
        query = select(cls.model.completed_projects).where(cls.model.id == user_id)
        completed_projects = await session.execute(query)
        return completed_projects.scalar_one_or_none()
