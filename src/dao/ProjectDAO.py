from sqlalchemy import func, or_, select  # noqa: N999
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.enums import ProjectStatusEnum
from db.models import Project
from schemas.projectSchema import ProjectCreate, ProjectListFilter, ProjectUpdate


class ProjectDAO:
    model = Project

    @classmethod
    async def create(
        cls, project_data: ProjectCreate, customer_id: int, session: AsyncSession
    ):
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
    async def get_by_id(cls, project_id: int, session: AsyncSession):
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
    async def update(
        cls, project_id: int, project_data: ProjectUpdate, session: AsyncSession
    ):
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
    async def delete(cls, project_id: int, session: AsyncSession):
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
    async def list(cls, session: AsyncSession, data: ProjectListFilter):
        query = select(cls.model)

        if data.category:
            query = query.where(cls.model.category == data.category)
        if data.status:
            query = query.where(cls.model.status == data.status)
        if data.budget_min:
            query = query.where(cls.model.budget >= data.budget_min)
        if data.budget_max:
            query = query.where(cls.model.budget <= data.budget_max)
        if data.search:
            query = query.where(
                or_(
                    cls.model.title.ilike(f"%{data.search}%"),
                    cls.model.description.ilike(f"%{data.search}%"),
                )
            )

        count_query = select(func.count()).select_from(cls.model)
        if data.category:
            count_query = count_query.where(cls.model.category == data.category)
        if data.status:
            count_query = count_query.where(cls.model.status == data.status)
        if data.budget_min:
            count_query = count_query.where(cls.model.budget >= data.budget_min)
        if data.budget_max:
            count_query = count_query.where(cls.model.budget <= data.budget_max)
        if data.search:
            count_query = count_query.where(
                or_(
                    cls.model.title.ilike(f"%{data.search}%"),
                    cls.model.description.ilike(f"%{data.search}%"),
                )
            )

        total = await session.scalar(count_query)

        offset = (data.page - 1) * data.page_size
        query = query.offset(offset).limit(data.page_size)

        result = await session.execute(query)
        projects = result.scalars().all()

        return projects, total

    @classmethod
    async def publish(cls, project_id: int, session: AsyncSession):
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
    async def complete(cls, project_id: int, session: AsyncSession):
        query = select(cls.model).where(
            cls.model.id == project_id,
            cls.model.status == ProjectStatusEnum.IN_PROGRESS,
        )
        project = await session.scalar(query)

        if project is None:
            return None

        project.status = ProjectStatusEnum.COMPLETED
        await session.commit()
        await session.refresh(project)
        return project

    @classmethod
    async def cancel(cls, project_id: int, session: AsyncSession):
        query = select(cls.model).where(
            cls.model.id == project_id,
            cls.model.status.in_(
                [ProjectStatusEnum.OPEN, ProjectStatusEnum.IN_PROGRESS]
            ),
        )
        project = await session.scalar(query)

        if project is None:
            return None

        project.status = ProjectStatusEnum.CANCELLED
        await session.commit()
        await session.refresh(project)
        return project

    @classmethod
    async def assign_freelancer(
        cls, project_id: int, freelancer_id: int, session: AsyncSession
    ):
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
    async def get_by_customer(
        cls, session: AsyncSession, customer_id: int, page: int = 1, page_size: int = 20
    ):
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
    async def get_by_freelancer(
        cls,
        session: AsyncSession,
        freelancer_id: int,
        page: int = 1,
        page_size: int = 20,
    ):
        query = (
            select(cls.model)
            .where(cls.model.freelancer_id == freelancer_id)
            .options(selectinload(cls.model.customer))
        )

        count_query = select(func.count()).where(
            cls.model.freelancer_id == freelancer_id
        )
        total = await session.scalar(count_query)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await session.execute(query)
        projects = result.scalars().all()

        return projects, total

    @classmethod
    async def get_open_projects(
        cls, session: AsyncSession, page: int = 1, page_size: int = 20
    ):
        query = (
            select(cls.model)
            .where(cls.model.status == ProjectStatusEnum.OPEN)
            .options(selectinload(cls.model.customer))
            .order_by(cls.model.created_at.desc())
        )

        count_query = select(func.count()).where(
            cls.model.status == ProjectStatusEnum.OPEN
        )
        total = await session.scalar(count_query)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await session.execute(query)
        projects = result.scalars().all()

        return projects, total

    @classmethod
    async def check_contract_exists(
        cls, project_id: int, session: AsyncSession
    ) -> bool:
        query = select(cls.model).where(
            cls.model.id == project_id,
            cls.model.contract.isnot(None),
        )
        project = await session.scalar(query)
        return project is not None
