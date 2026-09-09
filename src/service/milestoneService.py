from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessError, ConflictError, ForbiddenError, NotFoundError
from dao.ConractDAO import ContractDAO
from dao.MilestonDAO import MilestoneDAO
from db.enums import ContractStatusEnum, MilestoneStatusEnum
from db.models.userModel import User as UserModel
from schemas.milestoneSchema import MilestoneCreate, MilestoneResponse, MilestoneUpdate
from schemas.paginationSchema import PaginatedResponse


class MilestonService:
    @classmethod
    async def create_milestone(
        cls,
        session: AsyncSession,
        milestone_data: MilestoneCreate,
        contract_id: int,
        current_user: UserModel,
    ) -> MilestoneResponse:
        contract = await ContractDAO.get_by_id(contract_id=contract_id, session=session)
        if contract is None:
            raise NotFoundError("Contract not found")
        if contract.status != ContractStatusEnum.ACTIVE:
            raise BusinessError(
                "You cannot create milestone if you contract statut is not 'active'"
            )
        if contract.freelancer_id != current_user.id:
            raise ForbiddenError(
                "A user who is not a contract executor cannot create milestone"
            )
        milestone = await MilestoneDAO.create(
            milestone_data=milestone_data, contract_id=contract_id, session=session
        )
        return MilestoneResponse.model_validate(milestone)

    @classmethod
    async def get_milestone(
        cls, current_user: UserModel, milestone_id: int, session: AsyncSession
    ) -> MilestoneResponse:
        milestone = await MilestoneDAO.get_by_id(
            milestone_id=milestone_id, session=session
        )
        if milestone is None:
            raise NotFoundError("milestone not found")
        contract = await ContractDAO.get_by_id(
            contract_id=milestone.contract_id, session=session
        )
        if contract is None:
            raise ConflictError("contract is None")

        if (
            current_user.id != contract.freelancer_id
            and current_user.id != contract.customer_id
        ):
            raise ForbiddenError(
                "A user who is not a contract executor or customer cannot get milestone"
            )
        return MilestoneResponse.model_validate(milestone)

    @classmethod
    async def get_milestones_by_contract(
        cls,
        session: AsyncSession,
        contract_id: int,
        current_user: UserModel,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[MilestoneResponse]:
        contract = await ContractDAO.get_by_id(session=session, contract_id=contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")
        if (
            contract.customer_id != current_user.id
            and contract.freelancer_id != current_user.id
        ):
            raise BusinessError(
                "A user who is not a contract executor or customer cannot get milestones"
            )
        milestones, total = await MilestoneDAO.list_by_contract(
            session=session, contract_id=contract_id, page=page, page_size=page_size
        )
        if milestones is None:
            raise NotFoundError("milestones list is none")
        if total is None:
            raise ConflictError("total is none")

        validate_data = [MilestoneResponse.model_validate(i) for i in milestones]
        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def update_milestone(
        cls,
        current_user: UserModel,
        data: MilestoneUpdate,
        milestone_id: int,
        session: AsyncSession,
    ) -> MilestoneResponse:
        milestone = await MilestoneDAO.get_by_id(
            session=session, milestone_id=milestone_id
        )
        if milestone is None:
            raise NotFoundError("Milestone not found")
        contract = await ContractDAO.get_by_id(
            session=session, contract_id=milestone.contract_id
        )
        if contract is None:
            raise ConflictError("contract is none")
        if contract.freelancer_id != current_user.id:
            raise ForbiddenError(
                "A user who is not a contract executor cannot update milestone"
            )
        if milestone.status != MilestoneStatusEnum.PENDING:
            raise BusinessError(
                "You cannot change a milestone whose status is not 'pending'"
            )
        updated_milestone = await MilestoneDAO.update(
            milestone_data=data, session=session, milestone_id=milestone_id
        )
        return MilestoneResponse.model_validate(updated_milestone)

    @classmethod
    async def delete_milestone(
        cls,
        current_user: UserModel,
        milestone_id: int,
        session: AsyncSession,
    ) -> Literal[True]:
        milestone = await MilestoneDAO.get_by_id(
            session=session, milestone_id=milestone_id
        )
        if milestone is None:
            raise NotFoundError("Milestone not found")
        contract = await ContractDAO.get_by_id(
            session=session, contract_id=milestone.contract_id
        )
        if contract is None:
            raise ConflictError("contract is none")
        if contract.freelancer_id != current_user.id:
            raise ForbiddenError(
                "A user who is not a contract executor cannot delete milestone"
            )
        if milestone.status != MilestoneStatusEnum.PENDING:
            raise BusinessError(
                "You cannot delete a milestone whose status is not 'pending'"
            )
        result = await MilestoneDAO.delete(session=session, milestone_id=milestone_id)

        return result  # type: ignore

    @classmethod
    async def complete_milestone(
        cls,
        current_user: UserModel,
        milestone_id: int,
        session: AsyncSession,
    ) -> MilestoneResponse:
        milestone = await MilestoneDAO.get_by_id(
            session=session, milestone_id=milestone_id
        )
        if milestone is None:
            raise NotFoundError("Milestone not found")
        contract = await ContractDAO.get_by_id(
            session=session, contract_id=milestone.contract_id
        )
        if contract is None:
            raise ConflictError("contract is none")
        if contract.freelancer_id != current_user.id:
            raise ForbiddenError(
                "A user who is not a contract executor cannot compelete milestone"
            )
        if milestone.status != MilestoneStatusEnum.PENDING:
            raise BusinessError(
                "You cannot complete a milestone whose status is not 'pending'"
            )
        new_milestone = await MilestoneDAO.complete(
            session=session, milestone_id=milestone_id
        )

        return MilestoneResponse.model_validate(new_milestone)

    @classmethod
    async def approve_milestone(
        cls,
        current_user: UserModel,
        milestone_id: int,
        session: AsyncSession,
    ) -> MilestoneResponse:
        milestone = await MilestoneDAO.get_by_id(
            session=session, milestone_id=milestone_id
        )
        if milestone is None:
            raise NotFoundError("Milestone not found")
        contract = await ContractDAO.get_by_id(
            session=session, contract_id=milestone.contract_id
        )
        if contract is None:
            raise ConflictError("contract is none")
        if contract.customer_id != current_user.id:
            raise ForbiddenError(
                "A user who is not a contract customer cannot approved milestone"
            )
        if milestone.status != MilestoneStatusEnum.COMPLETED:
            raise BusinessError(
                "You cannot approve a milestone whose status is not 'compeleted'"
            )
        new_milestone = await MilestoneDAO.approve(
            session=session, milestone_id=milestone_id
        )

        return MilestoneResponse.model_validate(new_milestone)

    @classmethod
    async def check_all_approved(cls, session: AsyncSession, contract_id: int):
        result = await MilestoneDAO.check_all_approved(
            contract_id=contract_id, session=session
        )
        return result
