from sqlalchemy import select, func
from datetime import datetime

from db.models import Milestone
from db.database import async_session_maker
from db.enums import MilestoneStatusEnum
from schemas.milestone import MilestoneCreate, MilestoneUpdate


class MilestoneDAO:
    model = Milestone

    @classmethod
    async def create(cls, milestone_data: MilestoneCreate, contract_id: int):
        async with async_session_maker() as session:
            milestone = Milestone(
                **milestone_data.model_dump(),
                contract_id=contract_id,
                status=MilestoneStatusEnum.PENDING,
            )
            session.add(milestone)
            await session.commit()
            await session.refresh(milestone)
            return milestone

    @classmethod
    async def get_by_id(cls, milestone_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == milestone_id)
            return await session.scalar(query)

    @classmethod
    async def update(cls, milestone_id: int, milestone_data: MilestoneUpdate):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == milestone_id,
                cls.model.status == MilestoneStatusEnum.PENDING,
            )
            milestone = await session.scalar(query)

            if milestone is None:
                return None

            update_data = milestone_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(milestone, key, value)

            await session.commit()
            await session.refresh(milestone)
            return milestone

    @classmethod
    async def delete(cls, milestone_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == milestone_id,
                cls.model.status == MilestoneStatusEnum.PENDING,
            )
            milestone = await session.scalar(query)

            if milestone is None:
                return None

            await session.delete(milestone)
            await session.commit()
            return True

    @classmethod
    async def list_by_contract(cls, contract_id: int, page: int = 1, page_size: int = 20):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.contract_id == contract_id)

            count_query = select(func.count()).where(cls.model.contract_id == contract_id)
            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            milestones = result.scalars().all()

            return milestones, total

    @classmethod
    async def complete(cls, milestone_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == milestone_id,
                cls.model.status == MilestoneStatusEnum.PENDING,
            )
            milestone = await session.scalar(query)

            if milestone is None:
                return None

            milestone.status = MilestoneStatusEnum.COMPLETED
            await session.commit()
            await session.refresh(milestone)
            return milestone

    @classmethod
    async def approve(cls, milestone_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == milestone_id,
                cls.model.status == MilestoneStatusEnum.COMPLETED,
            )
            milestone = await session.scalar(query)

            if milestone is None:
                return None

            milestone.status = MilestoneStatusEnum.APPROVED
            await session.commit()
            await session.refresh(milestone)
            return milestone

    @classmethod
    async def get_pending_by_contract(cls, contract_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.contract_id == contract_id,
                cls.model.status == MilestoneStatusEnum.PENDING,
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_not_approved_by_contract(cls, contract_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.contract_id == contract_id,
                cls.model.status != MilestoneStatusEnum.APPROVED,
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def check_all_approved(cls, contract_id: int) -> bool:
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.contract_id == contract_id,
                cls.model.status != MilestoneStatusEnum.APPROVED,
            )
            milestone = await session.scalar(query)
            return milestone is None