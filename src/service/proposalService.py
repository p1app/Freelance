from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BusinessError, ConflictError, ForbiddenError, NotFoundError
from dao.ConractDAO import ContractDAO
from dao.ProjectDAO import ProjectDAO
from dao.ProposalDAO import ProposalDAO
from db.enums import ProjectStatusEnum, ProposalStatusEnum
from db.models.userModel import User as UserModel
from schemas.contractSchema import ContractCreate, ContractResponse
from schemas.paginationSchema import PaginatedResponse
from schemas.proposalSchema import ProposalCreate, ProposalResponse, ProposalUpdate
from service.contractService import ContractService
from service.projectService import ProjectService


class ProposalService:
    @classmethod
    async def create_proposal(
        cls,
        session: AsyncSession,
        data: ProposalCreate,
        project_id: int,
        freelancer_id: int,
    ) -> ProposalResponse:
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if project.status != ProjectStatusEnum.OPEN:
            raise BusinessError("Only OPEN projects can receive proposals")

        if project.customer_id == freelancer_id:
            raise BusinessError("The client cannot be the freelancer")

        existing_proposal = await ProposalDAO.get_by_freelancer_and_project(
            session=session, freelancer_id=freelancer_id, project_id=project_id
        )
        if existing_proposal:
            raise ConflictError(
                "You have already submitted a proposal for this project"
            )

        proposal = await ProposalDAO.create(
            session=session,
            proposal_data=data,
            project_id=project_id,
            freelancer_id=freelancer_id,
        )
        return ProposalResponse.model_validate(proposal)

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
        project = await ProjectDAO.get_by_id(session=session, project_id=project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if project.customer_id != current_user.id:
            raise ForbiddenError("Only the client can view proposals for this project")

        proposals, total = await ProposalDAO.list_by_project(
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
        proposal = await ProposalDAO.get_by_id(session=session, proposal_id=proposal_id)
        if proposal is None:
            raise NotFoundError("Proposal not found")

        if proposal.freelancer_id != current_user.id:
            raise ForbiddenError("You cannot update someone else's proposal")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be updated")

        updated_proposal = await ProposalDAO.update(
            session=session, proposal_id=proposal_id, proposal_data=data
        )
        return ProposalResponse.model_validate(updated_proposal)

    @classmethod
    async def withdraw_proposal(
        cls, session: AsyncSession, current_user: UserModel, proposal_id: int
    ) -> ProposalResponse:
        proposal = await ProposalDAO.get_by_id(session=session, proposal_id=proposal_id)
        if proposal is None:
            raise NotFoundError("Proposal not found")

        if proposal.freelancer_id != current_user.id:
            raise ForbiddenError("You cannot withdraw someone else's proposal")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be withdrawn")

        updated_proposal = await ProposalDAO.withdraw(
            session=session, proposal_id=proposal_id
        )
        return ProposalResponse.model_validate(updated_proposal)

    @classmethod
    async def accept_proposal(
        cls, session: AsyncSession, current_user: UserModel, proposal_id: int
    ) -> ContractResponse:
        proposal = await ProposalDAO.get_by_id(session=session, proposal_id=proposal_id)
        if proposal is None:
            raise NotFoundError("Proposal not found")

        project = await ProjectDAO.get_by_id(
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

        contract_exists = await ContractDAO.get_by_project(
            session=session, project_id=project.id
        )
        if contract_exists:
            raise BusinessError("This project already has a contract")

        await ProposalDAO.accept(session=session, proposal_id=proposal_id)

        await ProposalDAO.reject_others(
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
        proposal = await ProposalDAO.get_by_id(session=session, proposal_id=proposal_id)
        if proposal is None:
            raise NotFoundError("Proposal not found")

        project = await ProjectDAO.get_by_id(
            session=session, project_id=proposal.project_id
        )
        if project is None:
            raise NotFoundError("Project not found")

        if project.customer_id != current_user.id:
            raise ForbiddenError("Only the client can reject a proposal")

        if proposal.status != ProposalStatusEnum.PENDING:
            raise BusinessError("Only PENDING proposals can be rejected")

        rejected_proposal = await ProposalDAO.reject(
            session=session, proposal_id=proposal_id
        )
        return ProposalResponse.model_validate(rejected_proposal)
