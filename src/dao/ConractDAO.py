from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from db.models import Contract
from db.database import async_session_maker
from db.enums import ContractStatusEnum
from schemas.contract import ContractCreate


class ContractDAO:
    model = Contract

    @classmethod
    async def create(cls, contract_data: ContractCreate):
        async with async_session_maker() as session:
            contract = Contract(
                **contract_data.model_dump(),
                status=ContractStatusEnum.ACTIVE,
                start_date=datetime.now(),
            )
            session.add(contract)
            await session.commit()
            await session.refresh(contract)
            return contract

    @classmethod
    async def get_by_id(cls, contract_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == contract_id)
                .options(
                    selectinload(cls.model.project),
                    selectinload(cls.model.customer),
                    selectinload(cls.model.freelancer),
                    selectinload(cls.model.milestones),
                    selectinload(cls.model.reviews),
                    selectinload(cls.model.messages),
                )
            )
            return await session.scalar(query)

    @classmethod
    async def update(cls, contract_id: int, update_data: dict):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == contract_id)
            contract = await session.scalar(query)

            if contract is None:
                return None

            for key, value in update_data.items():
                setattr(contract, key, value)

            await session.commit()
            await session.refresh(contract)
            return contract

    @classmethod
    async def list_by_user(
        cls,
        user_id: int,
        role: str,  # "customer" or "freelancer"
        status: ContractStatusEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        async with async_session_maker() as session:
            if role == "customer":
                query = select(cls.model).where(cls.model.customer_id == user_id)
                count_query = select(func.count()).where(cls.model.customer_id == user_id)
            else:
                query = select(cls.model).where(cls.model.freelancer_id == user_id)
                count_query = select(func.count()).where(cls.model.freelancer_id == user_id)

            if status:
                query = query.where(cls.model.status == status)
                count_query = count_query.where(cls.model.status == status)

            total = await session.scalar(count_query)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            result = await session.execute(query)
            contracts = result.scalars().all()

            return contracts, total

    @classmethod
    async def complete(cls, contract_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == contract_id,
                cls.model.status == ContractStatusEnum.ACTIVE,
            )
            contract = await session.scalar(query)

            if contract is None:
                return None

            contract.status = ContractStatusEnum.COMPLETED
            contract.end_date = datetime.now()
            await session.commit()
            await session.refresh(contract)
            return contract

    @classmethod
    async def cancel(cls, contract_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(
                cls.model.id == contract_id,
                cls.model.status == ContractStatusEnum.ACTIVE,
            )
            contract = await session.scalar(query)

            if contract is None:
                return None

            contract.status = ContractStatusEnum.CANCELLED
            await session.commit()
            await session.refresh(contract)
            return contract

    @classmethod
    async def get_active_by_user(cls, user_id: int, role: str, page: int = 1, page_size: int = 20):
        return await cls.list_by_user(
            user_id=user_id,
            role=role,
            status=ContractStatusEnum.ACTIVE,
            page=page,
            page_size=page_size,
        )

    @classmethod
    async def get_by_project(cls, project_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.project_id == project_id)
            return await session.scalar(query)

    @classmethod
    async def get_completed_by_user(cls, user_id: int, role: str, page: int = 1, page_size: int = 20):
        return await cls.list_by_user(
            user_id=user_id,
            role=role,
            status=ContractStatusEnum.COMPLETED,
            page=page,
            page_size=page_size,
        )

    @classmethod
    async def check_milestones_approved(cls, contract_id: int) -> bool:
        async with async_session_maker() as session:
            from db.models import Milestone
            from db.enums import MilestoneStatusEnum

            query = select(cls.model).where(
                cls.model.id == contract_id,
                cls.model.milestones.any(
                    Milestone.status != MilestoneStatusEnum.APPROVED
                ),
            )
            contract = await session.scalar(query)
            return contract is None