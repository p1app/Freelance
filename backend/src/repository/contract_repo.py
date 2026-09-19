from datetime import datetime, timezone

from core.enums import ContractRoleUserEnum, ContractStatusEnum
from models import Contract
from schemas.contract_schema import ContractCreate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ContractRepository:
    model = Contract

    @classmethod
    async def create(cls, contract_data: ContractCreate, session: AsyncSession):
        contract = Contract(
            **contract_data.model_dump(),
            status=ContractStatusEnum.ACTIVE,
            start_date=datetime.now(timezone.utc),
        )
        session.add(contract)
        await session.flush()
        await session.refresh(contract)
        return contract

    @classmethod
    async def get_by_id(cls, contract_id: int, session: AsyncSession):
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
    async def list_by_user(
        cls,
        session: AsyncSession,
        user_id: int,
        role: ContractRoleUserEnum,
        status: ContractStatusEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        if role == ContractRoleUserEnum.CUSTOMER:
            query = select(cls.model).where(cls.model.customer_id == user_id)
            count_query = select(func.count()).where(cls.model.customer_id == user_id)
        if role == ContractRoleUserEnum.FREELANCER:
            query = select(cls.model).where(cls.model.freelancer_id == user_id)
            count_query = select(func.count()).where(cls.model.freelancer_id == user_id)

        if status:
            query = query.where(cls.model.status == status)
            count_query = count_query.where(cls.model.status == status)

        total = await session.scalar(count_query)

        offset = (page - 1) * page_size
        query = (
            query.offset(offset)
            .limit(page_size)
            .order_by(cls.model.created_at.desc(), cls.model.id.desc())
        )

        result = await session.execute(query)
        contracts = result.scalars().all()

        return contracts, total

    @classmethod
    async def complete(cls, contract_id: int, session: AsyncSession):
        query = select(cls.model).where(
            cls.model.id == contract_id,
            cls.model.status == ContractStatusEnum.ACTIVE,
        )
        contract = await session.scalar(query)

        if contract is None:
            return None

        contract.status = ContractStatusEnum.COMPLETED
        contract.end_date = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(contract)
        return contract

    @classmethod
    async def cancel(cls, contract_id: int, session: AsyncSession):
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
    async def get_active_by_user(
        cls,
        session: AsyncSession,
        user_id: int,
        role: ContractRoleUserEnum,
        page: int = 1,
        page_size: int = 20,
    ):
        return await cls.list_by_user(
            user_id=user_id,
            role=role,
            status=ContractStatusEnum.ACTIVE,
            page=page,
            page_size=page_size,
            session=session,
        )

    @classmethod
    async def get_by_project(cls, project_id: int, session: AsyncSession):
        query = select(cls.model).where(cls.model.project_id == project_id)
        return await session.scalar(query)
