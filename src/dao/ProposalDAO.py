from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession 

from db.models import Proposal
from db.enums import ProposalStatusEnum
from schemas.proposal import ProposalCreate, ProposalUpdate


class ProposalDAO:
    model = Proposal

    @classmethod
    async def create(cls, session: AsyncSession, proposal_data: ProposalCreate, project_id: int, freelancer_id: int):
        proposal = Proposal(
            **proposal_data.model_dump(),
            project_id=project_id,
            freelancer_id=freelancer_id,
            status=ProposalStatusEnum.PENDING,
        )
        session.add(proposal)
        await session.commit()
        await session.refresh(proposal)
        return proposal

    @classmethod
    async def get_by_id(cls, session: AsyncSession, proposal_id: int):
        query = (
            select(cls.model)
            .where(cls.model.id == proposal_id)
            .options(
                selectinload(cls.model.project),
                selectinload(cls.model.freelancer),
            )
        )
        return await session.scalar(query)

    @classmethod
    async def update(cls, session: AsyncSession, proposal_id: int, proposal_data: ProposalUpdate):
        query = select(cls.model).where(
            cls.model.id == proposal_id,
            cls.model.status == ProposalStatusEnum.PENDING,
        )
        proposal = await session.scalar(query)

        if proposal is None:
            return None

        update_data = proposal_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(proposal, key, value)

        await session.commit()
        await session.refresh(proposal)
        return proposal

    @classmethod
    async def delete(cls, session: AsyncSession, proposal_id: int):
        query = select(cls.model).where(
            cls.model.id == proposal_id,
            cls.model.status.in_([ProposalStatusEnum.PENDING, ProposalStatusEnum.WITHDRAWN]),
        )
        proposal = await session.scalar(query)

        if proposal is None:
            return None

        await session.delete(proposal)
        await session.commit()
        return True

    @classmethod
    async def list_by_project(
        cls,
        session: AsyncSession,
        project_id: int,
        status: ProposalStatusEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        query = (
            select(cls.model)
            .where(cls.model.project_id == project_id)
            .options(selectinload(cls.model.freelancer))
        )

        if status:
            query = query.where(cls.model.status == status)

        count_query = select(func.count()).where(cls.model.project_id == project_id)
        if status:
            count_query = count_query.where(cls.model.status == status)

        total = await session.scalar(count_query)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await session.execute(query)
        proposals = result.scalars().all()

        return proposals, total

    @classmethod
    async def accept(cls, session: AsyncSession, proposal_id: int):
        query = select(cls.model).where(
            cls.model.id == proposal_id,
            cls.model.status == ProposalStatusEnum.PENDING,
        )
        proposal = await session.scalar(query)

        if proposal is None:
            return None

        proposal.status = ProposalStatusEnum.ACCEPTED
        await session.commit()
        await session.refresh(proposal)
        return proposal

    @classmethod
    async def reject(cls, session: AsyncSession, proposal_id: int):
        query = select(cls.model).where(
            cls.model.id == proposal_id,
            cls.model.status == ProposalStatusEnum.PENDING,
        )
        proposal = await session.scalar(query)

        if proposal is None:
            return None

        proposal.status = ProposalStatusEnum.REJECTED
        await session.commit()
        await session.refresh(proposal)
        return proposal

    @classmethod
    async def withdraw(cls, session: AsyncSession, proposal_id: int):
        query = select(cls.model).where(
            cls.model.id == proposal_id,
            cls.model.status == ProposalStatusEnum.PENDING,
        )
        proposal = await session.scalar(query)

        if proposal is None:
            return None

        proposal.status = ProposalStatusEnum.WITHDRAWN
        await session.commit()
        await session.refresh(proposal)
        return proposal

    @classmethod
    async def reject_others(cls, session: AsyncSession, project_id: int, exclude_proposal_id: int):
        query = select(cls.model).where(
            cls.model.project_id == project_id,
            cls.model.id != exclude_proposal_id,
            cls.model.status == ProposalStatusEnum.PENDING,
        )
        proposals = await session.scalars(query)

        for proposal in proposals:
            proposal.status = ProposalStatusEnum.REJECTED

        await session.commit()

    @classmethod
    async def get_by_freelancer_and_project(cls, session: AsyncSession, freelancer_id: int, project_id: int):
        query = select(cls.model).where(
            cls.model.freelancer_id == freelancer_id,
            cls.model.project_id == project_id,
            cls.model.status != ProposalStatusEnum.WITHDRAWN,
        )
        return await session.scalar(query)

    @classmethod
    async def get_pending_by_project(cls, session: AsyncSession, project_id: int):
        query = select(cls.model).where(
            cls.model.project_id == project_id,
            cls.model.status == ProposalStatusEnum.PENDING,
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_accepted_by_project(cls, session: AsyncSession, project_id: int):
        query = select(cls.model).where(
            cls.model.project_id == project_id,
            cls.model.status == ProposalStatusEnum.ACCEPTED,
        )
        return await session.scalar(query)