from core.enums import ProjectStatusEnum, ProposalStatusEnum, RoleEnum
from core.exceptions import BusinessError, ConflictError, ForbiddenError, NotFoundError
from models.user_model import User as UserModel
from repository.contract_repo import ContractRepository
from repository.project_repo import ProjectRepository
from repository.proposal_repo import ProposalRepository
from schemas.contract_schema import ContractCreate, ContractResponse
from schemas.pagination_schema import PaginatedResponse
from schemas.proposal_schema import (
    ProposalCreate,
    ProposalResponse,
    ProposalUpdate,
)
from service.contract_service import ContractService
from service.project_service import ProjectService
from sqlalchemy.ext.asyncio import AsyncSession


class ProposalService:
    @classmethod
    async def create_proposal(
        cls,
        session: AsyncSession,
        data: ProposalCreate,
        project_id: int,
        freelancer_id: int,
    ) -> ProposalResponse:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        if project is None:
            raise NotFoundError("Project not found")

        if project.status != ProjectStatusEnum.OPEN:
            raise BusinessError("Only OPEN projects can receive proposals")

        if project.customer_id == freelancer_id:
            raise BusinessError("The client cannot be the freelancer")

        existing_proposal = await ProposalRepository.get_by_freelancer_and_project(
            session=session, freelancer_id=freelancer_id, project_id=project_id
        )
        if existing_proposal:
            raise ConflictError(
                "You have already submitted a proposal for this project"
            )

        proposal = await ProposalRepository.create(
            session=session,
            proposal_data=data,
            project_id=project_id,
            freelancer_id=freelancer_id,
        )
        proposal_dict = proposal.__dict__.copy()
        proposal_dict["freelancer_name"] = proposal.freelancer.fullname
        return ProposalResponse.model_validate(proposal_dict)

    @classmethod
    async def get_proposals_by_project(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        project_id: int,
        status: ProposalStatusEnum | None,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[ProposalResponse]:
        project = await ProjectRepository.get_by_id(
            session=session, project_id=project_id
        )
        if project is None:
            raise NotFoundError("Project not found")

        if (
            project.customer_id != current_user.id
            and current_user.role != RoleEnum.ADMIN
        ):
            raise ForbiddenError("Only the client can view proposals for this project")

        proposals, total = await ProposalRepository.list_by_project(
            session=session,
            project_id=project_id,
            status=status,
            page=page,
            page_size=page_size,
        )

        if total is None:
            raise ConflictError("total is None")

        validate_data = [
            ProposalResponse.model_validate(proposal) for proposal in proposals
        ]

        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )

    @classmethod
    async def update_proposal(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        proposal_id: int,
        data: ProposalUpdate,
    ) -> ProposalResponse:
        proposal = await ProposalRepository.get_by_id(
            session=session, proposal_id=proposal_id
        )
        if proposal is None:
            raise NotFoundError("Proposal not found")

        if proposal.freelancer_id != current_user.id:
            raise ForbiddenError("You cannot update someone else's proposal")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be updated")

        updated_proposal = await ProposalRepository.update(
            session=session, proposal_id=proposal_id, proposal_data=data
        )
        return ProposalResponse.model_validate(updated_proposal)

    @classmethod
    async def withdraw_proposal(
        cls, session: AsyncSession, current_user: UserModel, proposal_id: int
    ) -> ProposalResponse:
        proposal = await ProposalRepository.get_by_id(
            session=session, proposal_id=proposal_id
        )
        if proposal is None:
            raise NotFoundError("Proposal not found")

        if proposal.freelancer_id != current_user.id:
            raise ForbiddenError("You cannot withdraw someone else's proposal")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be withdrawn")

        updated_proposal = await ProposalRepository.withdraw(
            session=session, proposal_id=proposal_id
        )
        return ProposalResponse.model_validate(updated_proposal)

    @classmethod
    async def accept_proposal(
        cls, session: AsyncSession, current_user: UserModel, proposal_id: int
    ) -> ContractResponse:
        proposal = await ProposalRepository.get_by_id(
            session=session, proposal_id=proposal_id
        )
        if proposal is None:
            raise NotFoundError("Proposal not found")

        project = await ProjectRepository.get_by_id(
            session=session, project_id=proposal.project_id
        )
        if project is None:
            raise NotFoundError("Project not found")

        if project.customer_id != current_user.id:
            raise ForbiddenError("Only the client can accept a proposal")

        if project.status != ProjectStatusEnum.OPEN:
            raise BusinessError("Only OPEN projects can accept proposals")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be accepted")

        if project.customer_id == proposal.freelancer_id:
            raise BusinessError("The client cannot accept their own proposal")

        contract_exists = await ContractRepository.get_by_project(
            session=session, project_id=project.id
        )
        if contract_exists:
            raise BusinessError("This project already has a contract")

        await ProposalRepository.accept(session=session, proposal_id=proposal_id)

        await ProposalRepository.reject_others(
            session=session,
            project_id=proposal.project_id,
            exclude_proposal_id=proposal_id,
        )

        await ProjectService.assign_freelancer(
            session=session,
            current_user=current_user,
            project_id=proposal.project_id,
            freelancer_id=proposal.freelancer_id,
        )

        contract_data = ContractCreate(
            proposal_id=proposal_id,
            project_id=proposal.project_id,
            customer_id=project.customer_id,
            freelancer_id=proposal.freelancer_id,
            final_price=proposal.bid_amount,
        )

        contract = await ContractService.create_contract(
            session=session, contract_data=contract_data
        )
        return contract

    @classmethod
    async def reject_proposal(
        cls, session: AsyncSession, current_user: UserModel, proposal_id: int
    ) -> ProposalResponse:
        proposal = await ProposalRepository.get_by_id(
            session=session, proposal_id=proposal_id
        )
        if proposal is None:
            raise NotFoundError("Proposal not found")

        project = await ProjectRepository.get_by_id(
            session=session, project_id=proposal.project_id
        )
        if project is None:
            raise NotFoundError("Project not found")

        if project.customer_id != current_user.id:
            raise ForbiddenError("Only the client can reject a proposal")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be rejected")

        rejected_proposal = await ProposalRepository.reject(
            session=session, proposal_id=proposal_id
        )
        return ProposalResponse.model_validate(rejected_proposal)

    @classmethod
    async def get_my_proposal(
        cls,
        session: AsyncSession,
        current_user: UserModel,
        status: ProposalStatusEnum | None,
        page: int,
        page_size: int,
    ):
        if current_user.role != RoleEnum.FREELANCER:
            raise ForbiddenError("Only freelancer have proposals")
        proposals, total = await ProposalRepository.list_by_freelancer(
            session=session,
            freelancer_id=current_user.id,
            status=status,
            page=page,
            page_size=page_size,
        )
        if proposals is None:
            proposals = []
        if total is None:
            total = 0

        validate_data = [ProposalResponse.model_validate(i) for i in proposals]
        return PaginatedResponse(
            items=validate_data,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size,
        )
