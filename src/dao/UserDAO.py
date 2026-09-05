from sqlalchemy import select
from sqlalchemy import func

from db.models import User
from db.database import async_session_maker
from schemas.user import UserUpdate
from schemas.auth import UserRegister
from db.enums import RoleEnum


class UserDAO:
    model = User

    @classmethod
    async def create(cls, user_data: UserRegister):
        async with async_session_maker() as session:
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
    async def get_by_id(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == user_id)
            return await session.scalar(query)

    @classmethod
    async def get_by_email(cls, email: str):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.email == email)
            return await session.scalar(query)

    @classmethod
    async def get_by_username(cls, username: str):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.username == username)
            return await session.scalar(query)

    @classmethod
    async def update(cls, user_id: int, user_data: UserUpdate):
        async with async_session_maker() as session:
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
    async def delete(cls, user_id: int):
        async with async_session_maker() as session:
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
    async def block(cls, user_id: int):
        async with async_session_maker() as session:
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
    async def unblock(cls, user_id: int):
        async with async_session_maker() as session:
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
        page: int = 1,
        page_size: int = 20,
        role: RoleEnum | None = None,
        is_active: bool | None = None,
    ):
        async with async_session_maker() as session:
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
    async def get_freelancers(
        cls,
        skills: list[str] | None = None,
        min_rating: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.role == RoleEnum.FREELANCER)

            if min_rating is not None:
                query = query.where(cls.model.rating >= min_rating)

            if skills:
                conditions = []
                for skill in skills:
                    conditions.append(cls.model.skills.any(func.lower(skill)))
                query = query.where(func.or_(*conditions))

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            users = result.scalars().all()

            count_query = select(func.count()).where(cls.model.role == RoleEnum.FREELANCER)
            if min_rating is not None:
                count_query = count_query.where(cls.model.rating >= min_rating)
            if skills:
                conditions = []
                for skill in skills:
                    conditions.append(cls.model.skills.any(func.lower(skill)))
                count_query = count_query.where(func.or_(*conditions))

            total = await session.scalar(count_query)

            return users, total

    @classmethod
    async def search_by_skills(cls, skills: list[str], page: int = 1, page_size: int = 20):
        return await cls.get_freelancers(skills=skills, page=page, page_size=page_size)