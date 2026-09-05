from sqlalchemy import select, func

from db.models import User, Project
from db.database import async_session_maker
from db.enums import RoleEnum, ProjectStatusEnum, ContractStatusEnum


class AdminDAO:
    @classmethod
    async def list_users(cls, role: RoleEnum | None = None, is_active: bool | None = None, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = select(User)

            if role:
                query = query.where(User.role == role)
            if is_active is not None:
                query = query.where(User.is_active == is_active)

            count_query = select(func.count()).select_from(User)
            if role:
                count_query = count_query.where(User.role == role)
            if is_active is not None:
                count_query = count_query.where(User.is_active == is_active)

            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            users = result.scalars().all()

            return users, total

    @classmethod
    async def block_user(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(User).where(
                User.id == user_id,
                User.is_active == True,
            )
            user = await session.scalar(query)

            if user is None:
                return None

            user.is_active = False
            await session.commit()
            return True

    @classmethod
    async def unblock_user(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(User).where(
                User.id == user_id,
                User.is_active == False,
            )
            user = await session.scalar(query)

            if user is None:
                return None

            user.is_active = True
            await session.commit()
            return True

    @classmethod
    async def list_projects(cls, status: ProjectStatusEnum | None = None, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = select(Project)

            if status:
                query = query.where(Project.status == status)

            count_query = select(func.count()).select_from(Project)
            if status:
                count_query = count_query.where(Project.status == status)

            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            projects = result.scalars().all()

            return projects, total

    @classmethod
    async def delete_project(cls, project_id: int):
        async with async_session_maker() as session:
            query = select(Project).where(Project.id == project_id)
            project = await session.scalar(query)

            if project is None:
                return None

            await session.delete(project)
            await session.commit()
            return True

    @classmethod
    async def get_stats(cls):
        async with async_session_maker() as session:
            stats = {}

            # Пользователи
            stats["total_users"] = await session.scalar(select(func.count()).select_from(User))
            stats["clients_count"] = await session.scalar(
                select(func.count()).where(User.role == RoleEnum.CLIENT)
            )
            stats["freelancers_count"] = await session.scalar(
                select(func.count()).where(User.role == RoleEnum.FREELANCER)
            )

            # Проекты
            stats["total_projects"] = await session.scalar(select(func.count()).select_from(Project))
            stats["open_projects"] = await session.scalar(
                select(func.count()).where(Project.status == ProjectStatusEnum.OPEN)
            )
            stats["in_progress_projects"] = await session.scalar(
                select(func.count()).where(Project.status == ProjectStatusEnum.IN_PROGRESS)
            )
            stats["completed_projects"] = await session.scalar(
                select(func.count()).where(Project.status == ProjectStatusEnum.COMPLETED)
            )

            # Контракты
            from db.models import Contract
            stats["total_contracts"] = await session.scalar(select(func.count()).select_from(Contract))
            stats["active_contracts"] = await session.scalar(
                select(func.count()).where(Contract.status == ContractStatusEnum.ACTIVE)
            )

            # Средний рейтинг фрилансеров
            avg_rating = await session.scalar(
                select(func.avg(User.rating)).where(User.role == RoleEnum.FREELANCER)
            )
            stats["average_rating"] = avg_rating or 0.0

            return stats