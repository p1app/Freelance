from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from db.models import Project
from db.database import async_session_maker
from db.enums import ProjectCategoryEnum, ProjectStatusEnum
from schemas.project import ProjectCreate, ProjectUpdate


class ProjectDAO:
    model = Project

    @classmethod
    async def create(cls, project_data: ProjectCreate, customer_id: int):
        async with async_session_maker() as session:
            project = Project(
                **project_data.model_dump(),
                customer_id=customer_id,
                status=ProjectStatusEnum.DRAFT,
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project

    @classmethod
    async def get_by_id(cls, project_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == project_id)
                .options(
                    selectinload(cls.model.customer),
                    selectinload(cls.model.freelancer),
                    selectinload(cls.model.proposals),
                    selectinload(cls.model.contract),
                )
            )
            return await session.scalar(query)

    @classmethod
    async def update(cls, project_id: int, project_data: ProjectUpdate):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == project_id)
            project = await session.scalar(query)

            if project is None:
                return None

            update_data = project_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(project, key, value)

            await session.commit()
            await session.refresh(project)
            return project

    @classmethod
    async def delete(cls, project_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == project_id,
                cls.model.status.in_([ProjectStatusEnum.DRAFT, ProjectStatusEnum.OPEN]),
            )
            project = await session.scalar(query)

            if project is None:
                return None

            await session.delete(project)
            await session.commit()
            return True

    @classmethod
    async def list(
        cls,
        category: ProjectCategoryEnum | None = None,
        status: ProjectStatusEnum | None = None,
        budget_min: int | None = None,
        budget_max: int | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        async with async_session_maker() as session:
            query = select(cls.model)

            if category:
                query = query.where(cls.model.category == category)
            if status:
                query = query.where(cls.model.status == status)
            if budget_min:
                query = query.where(cls.model.budget >= budget_min)
            if budget_max:
                query = query.where(cls.model.budget <= budget_max)
            if search:
                query = query.where(
                    or_(
                        cls.model.title.ilike(f"%{search}%"),
                        cls.model.description.ilike(f"%{search}%"),
                    )
                )

            count_query = select(func.count()).select_from(cls.model)
            if category:
                count_query = count_query.where(cls.model.category == category)
            if status:
                count_query = count_query.where(cls.model.status == status)
            if budget_min:
                count_query = count_query.where(cls.model.budget >= budget_min)
            if budget_max:
                count_query = count_query.where(cls.model.budget <= budget_max)
            if search:
                count_query = count_query.where(
                    or_(
                        cls.model.title.ilike(f"%{search}%"),
                        cls.model.description.ilike(f"%{search}%"),
                    )
                )

            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            projects = result.scalars().all()

            return projects, total

    @classmethod
    async def publish(cls, project_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == project_id,
                cls.model.status == ProjectStatusEnum.DRAFT,
            )
            project = await session.scalar(query)

            if project is None:
                return None

            project.status = ProjectStatusEnum.OPEN
            await session.commit()
            await session.refresh(project)
            return project

    @classmethod
    async def cancel(cls, project_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == project_id,
                cls.model.status.in_([ProjectStatusEnum.OPEN, ProjectStatusEnum.IN_PROGRESS]),
            )
            project = await session.scalar(query)

            if project is None:
                return None

            project.status = ProjectStatusEnum.CANCELLED
            await session.commit()
            await session.refresh(project)
            return project

    @classmethod
    async def assign_freelancer(cls, project_id: int, freelancer_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == project_id,
                cls.model.status == ProjectStatusEnum.OPEN,
            )
            project = await session.scalar(query)

            if project is None:
                return None

            project.status = ProjectStatusEnum.IN_PROGRESS
            project.freelancer_id = freelancer_id
            await session.commit()
            await session.refresh(project)
            return project

    @classmethod
    async def get_by_customer(cls, customer_id: int, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.customer_id == customer_id)
                .options(selectinload(cls.model.freelancer))
            )

            count_query = select(func.count()).where(cls.model.customer_id == customer_id)
            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            projects = result.scalars().all()

            return projects, total

    @classmethod
    async def get_by_freelancer(cls, freelancer_id: int, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.freelancer_id == freelancer_id)
                .options(selectinload(cls.model.customer))
            )

            count_query = select(func.count()).where(cls.model.freelancer_id == freelancer_id)
            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            projects = result.scalars().all()

            return projects, total

    @classmethod
    async def get_open_projects(cls, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.status == ProjectStatusEnum.OPEN)
                .options(selectinload(cls.model.customer))
                .order_by(cls.model.created_at.desc())
            )

            count_query = select(func.count()).where(cls.model.status == ProjectStatusEnum.OPEN)
            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            projects = result.scalars().all()

            return projects, total

    @classmethod
    async def check_contract_exists(cls, project_id: int) -> bool:
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == project_id,
                cls.model.contract.isnot(None),
            )
            project = await session.scalar(query)
            return project is not None